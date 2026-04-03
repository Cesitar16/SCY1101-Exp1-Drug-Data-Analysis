import csv
import shutil
from pathlib import Path

try:
    import pandas as pd
except ImportError:
    pd = None


PROJECT_ROOT = Path(__file__).resolve().parents[1]
RAW_DATA_DIR = PROJECT_ROOT / "data" / "raw"
RAW_DATA_PATH = RAW_DATA_DIR / "Medicine_Details.csv"
DATASET_HANDLE = "aadyasingh55/drug-dataset"


def _resolve_path(path: str | Path) -> Path:
    resolved_path = Path(path)
    if not resolved_path.is_absolute():
        resolved_path = PROJECT_ROOT / resolved_path
    return resolved_path


def download_medicine_data(
    dataset_handle: str = DATASET_HANDLE,
    filename: str = RAW_DATA_PATH.name,
    destination: str | Path = RAW_DATA_PATH,
    force: bool = False,
) -> Path:
    """Descarga el dataset con kagglehub y copia el CSV al proyecto."""
    destination_path = _resolve_path(destination)
    destination_path.parent.mkdir(parents=True, exist_ok=True)

    if destination_path.exists() and destination_path.stat().st_size > 0 and not force:
        return destination_path

    try:
        import kagglehub
    except ImportError as exc:
        raise ImportError(
            "No se encontro 'kagglehub'. Instala las dependencias con: "
            "pip install -r requirements.txt"
        ) from exc

    download_dir = Path(kagglehub.dataset_download(dataset_handle))
    source_path = download_dir / filename

    if not source_path.exists():
        matches = list(download_dir.rglob(filename))
        if not matches:
            raise FileNotFoundError(
                f"No se encontro '{filename}' dentro del dataset descargado en: "
                f"{download_dir}"
            )
        source_path = matches[0]

    shutil.copy2(source_path, destination_path)
    return destination_path


def load_medicine_data(
    path: str | Path = RAW_DATA_PATH,
    download_if_missing: bool = False,
    force_download: bool = False,
):
    """Carga el CSV desde data/raw y opcionalmente lo descarga primero."""
    csv_path = _resolve_path(path)

    needs_download = (not csv_path.exists()) or csv_path.stat().st_size == 0
    if download_if_missing and (needs_download or force_download):
        csv_path = download_medicine_data(
            filename=csv_path.name,
            destination=csv_path,
            force=force_download,
        )

    if not csv_path.exists():
        raise FileNotFoundError(
            f"No se encontro el archivo de datos en: {csv_path}"
        )

    if csv_path.stat().st_size == 0:
        return pd.DataFrame() if pd is not None else []

    if pd is not None:
        return pd.read_csv(csv_path)

    with csv_path.open(mode="r", encoding="utf-8-sig", newline="") as file:
        return list(csv.DictReader(file))


def main() -> None:
    try:
        data = load_medicine_data(download_if_missing=True)
    except Exception as exc:
        raise SystemExit(f"Error al preparar la data: {exc}") from exc

    row_count = data.shape[0] if pd is not None else len(data)

    print(f"Archivo listo en: {RAW_DATA_PATH}")
    print(f"Registros leidos: {row_count}")


if __name__ == "__main__":
    main()
