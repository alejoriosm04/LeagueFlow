from datetime import UTC, datetime

from src.exports.csv_serializer import CsvDocument, crear_csv


def test_csv_usa_bom_crlf_metadatos_quoting_y_neutraliza_formulas():
    generado = datetime(2026, 8, 22, 15, 30, tzinfo=UTC)
    documento = crear_csv(
        league_name='Liga, "Especial"',
        resource="clasificacion",
        headers=["Equipo", "Nota"],
        rows=[["Águilas", "línea 1\nlínea 2"], ["=2+2", "+SUM(A1:A2)"]],
        now=lambda: generado,
    )

    assert isinstance(documento, CsvDocument)
    assert documento.content.startswith(b"\xef\xbb\xbf")
    texto = documento.content.decode("utf-8-sig")
    assert texto.count("\r\n") == 6
    assert texto.replace("\r\n", "").count("\n") == 1  # salto dentro de una celda quoted
    assert 'Liga,"Liga, ""Especial"""' in texto
    assert '"línea 1\nlínea 2"' in texto
    assert "'=2+2" in texto and "'+SUM(A1:A2)" in texto
    assert documento.filename == "liga-especial-clasificacion-2026-08-22.csv"
    assert documento.media_type == "text/csv; charset=utf-8"


def test_csv_vacio_conserva_metadatos_y_encabezados():
    documento = crear_csv(
        league_name="Liga vacía",
        resource="calendario",
        headers=["Local", "Visitante"],
        rows=[],
        now=lambda: datetime(2026, 8, 22, tzinfo=UTC),
    )
    assert documento.content.decode("utf-8-sig").endswith("Local,Visitante\r\n")
