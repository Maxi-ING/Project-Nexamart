"""Exporta datos y lógica del PBIX recibido. No sustituye al ETL original."""

import argparse
import hashlib
import json
import shutil
import zipfile
from decimal import Decimal
from importlib.metadata import version
from pathlib import Path

import pandas as pd
from pbixray import PBIXRay


TABLES = {
    "dimtienda": "tienda_id",
    "dimvendedor": "vendedor_id",
    "dimproducto": "producto_id",
    "dimcliente": "cliente_id",
    "dimmetodopago": "metodo_pago_id",
    "factventas": "order_id",
}


def cents(value):
    return int(Decimal(str(value)).quantize(Decimal("0.01")) * 100)


def amount(series):
    return sum(cents(value) for value in series)


def literal(value):
    if pd.isna(value):
        return "NULL"
    if isinstance(value, pd.Timestamp):
        return "'" + value.strftime("%Y-%m-%d") + "'"
    if isinstance(value, str):
        # Hexadecimal evita depender del modo de escape de MySQL.
        return "CONVERT(0x" + value.encode("utf-8").hex() + " USING utf8mb4)" if value else "''"
    if isinstance(value, bool):
        return "1" if value else "0"
    if isinstance(value, float):
        return format(Decimal(str(value)).quantize(Decimal("0.01")), "f")
    return str(int(value))


def export(pbix, destination):
    model = PBIXRay(str(pbix))
    snapshots = destination / "data" / "snapshot"
    powerbi = destination / "powerbi"
    sql = destination / "sql"
    for folder in (snapshots, powerbi, sql):
        folder.mkdir(parents=True, exist_ok=True)
    frames = {name: model.get_table("nexamart " + name) for name in TABLES}
    for name, frame in frames.items():
        key = TABLES[name]
        if frame[key].isna().any() or frame[key].duplicated().any():
            raise ValueError("Clave inválida: " + name)
    facts = frames["factventas"]
    for name, key in TABLES.items():
        if name != "factventas" and not facts[key].isin(frames[name][key]).all():
            raise ValueError("Hechos sin dimensión: " + name)
    vendors = frames["dimvendedor"]
    if not vendors.loc[vendors.tienda_id.notna(), "tienda_id"].isin(frames["dimtienda"].tienda_id).all():
        raise ValueError("Vendedor sin tienda existente")
    if not (facts.es_devolucion == (facts.cantidad < 0)).all():
        raise ValueError("Devoluciones incoherentes con cantidad")
    if not all(cents(row.precio_total) == cents(Decimal(str(row.precio_unitario)) * int(row.cantidad))
               for row in facts.itertuples()):
        raise ValueError("Importes incoherentes con precio por cantidad")

    sales = facts.loc[~facts.es_devolucion]
    returns = facts.loc[facts.es_devolucion]
    metrics = {
        "registros": len(facts),
        "order_id_distintos": int(facts.order_id.nunique()),
        "ventas_sin_devoluciones_registros": len(sales),
        "devoluciones_registros": len(returns),
        "ventas_sin_devoluciones_centavos": amount(sales.precio_total),
        "devoluciones_centavos": amount(returns.precio_total),
        "ventas_netas_centavos": amount(facts.precio_total),
        "unidades_netas": int(facts.cantidad.sum()),
        "sin_cliente_identificado": int((facts.cliente_id == -1).sum()),
        "sin_vendedor_identificado": int((facts.vendedor_id == -1).sum()),
        "fecha_min": facts.fecha.min().strftime("%Y-%m-%d"),
        "fecha_max": facts.fecha.max().strftime("%Y-%m-%d"),
    }
    if metrics["ventas_netas_centavos"] != metrics["ventas_sin_devoluciones_centavos"] + metrics["devoluciones_centavos"]:
        raise ValueError("Conciliación de importes fallida")

    for name, frame in frames.items():
        frame = frame.sort_values(TABLES[name])
        frame.to_csv(snapshots / (name + ".csv"), index=False, date_format="%Y-%m-%d", float_format="%.2f")
    calendar = model.get_table("DimCalendario")
    calendar.sort_values("Date").to_csv(snapshots / "dimcalendario.csv", index=False, date_format="%Y-%m-%d")

    dax = ["// Expresiones originales extraídas del PBIX. No es un script de creación de modelo.\n"]
    for measure in model.dax_measures.to_dict("records"):
        dax.append("// Tabla: " + measure["TableName"] + "\n" + measure["Name"] + " =\n" + measure["Expression"].strip() + "\n")
    (powerbi / "medidas_originales.dax").write_text("\n".join(dax), encoding="utf-8")
    calendar_expression = model.dax_tables.loc[model.dax_tables.TableName == "DimCalendario", "Expression"].iloc[0]
    (powerbi / "calendario_original.dax").write_text("// Expresión original extraída del PBIX.\nDimCalendario =\n" + calendar_expression.strip() + "\n", encoding="utf-8")
    relationships = model.relationships[["FromTableName", "FromColumnName", "ToTableName", "ToColumnName", "IsActive", "Cardinality", "CrossFilteringBehavior"]]
    (powerbi / "relaciones_originales.json").write_text(relationships.to_json(orient="records", force_ascii=False, indent=2) + "\n", encoding="utf-8")
    with zipfile.ZipFile(pbix) as archive:
        theme_files = [name for name in archive.namelist() if "RegisteredResources/" in name and name.endswith(".json")]
        custom_themes = [json.loads(archive.read(name)) for name in theme_files]
        theme = next(theme for theme in custom_themes if "dataColors" in theme)
        (powerbi / "tema_nexamart.json").write_text(json.dumps(theme, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    target = powerbi / "NexaMart.pbix"
    if pbix.resolve() != target.resolve():
        shutil.copyfile(pbix, target)

    statements = [
        "-- NexaMart | Carga del snapshot extraído del PBIX recibido.",
        "-- No es la carga original del ETL; conserva los datos importados del informe.",
        "-- Ejecutar después de nexamart_schema.sql, con las seis tablas vacías.",
        "-- No borra datos ni reemplaza claves existentes; no ejecutar dos veces.",
        "USE nexamart;", "START TRANSACTION;",
    ]
    for name in TABLES:
        frame = frames[name].sort_values(TABLES[name])
        columns = ", ".join("`" + col + "`" for col in frame.columns)
        rows = frame.itertuples(index=False, name=None)
        values = ["(" + ", ".join(literal(value) for value in row) + ")" for row in rows]
        statements.append("-- " + name + ": " + str(len(frame)) + " registros.")
        for offset in range(0, len(values), 100):
            statements.append("INSERT INTO `" + name + "` (" + columns + ") VALUES\n" + ",\n".join(values[offset:offset + 100]) + ";")
    statements.append("COMMIT;")
    (sql / "nexamart_snapshot_data.sql").write_text("\n\n".join(statements) + "\n", encoding="utf-8")
    manifest = {
        "origen": "Datos y metadatos recuperados del PBIX aportado por el autor",
        "archivo": "powerbi/NexaMart.pbix",
        "sha256_pbix": hashlib.sha256(pbix.read_bytes()).hexdigest(),
        "lector": "pbixray " + version("pbixray"),
        "filas_por_tabla": {name: len(frame) for name, frame in frames.items()},
        "filas_calendario": len(calendar),
        "medidas_dax": len(model.dax_measures),
        "relaciones_base_recuperadas": len(relationships),
        "relacion_calendario_hechos_presente": bool(((relationships.FromTableName == "DimCalendario") | (relationships.ToTableName == "DimCalendario")).any()),
        "metricas": metrics,
        "controles": {"claves_unicas": True, "integridad_dimensional": True, "precio_por_cantidad": True, "devoluciones_por_signo": True, "conciliacion_importes": True},
    }
    (snapshots / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(manifest, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--pbix", type=Path, required=True)
    parser.add_argument("--destino", type=Path, required=True)
    args = parser.parse_args()
    export(args.pbix, args.destino)
