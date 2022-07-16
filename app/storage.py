from depot.manager import DepotManager


def configure_storage():
    DepotManager.configure("default", {"depot.storage_path": f"~/assets/fastauto"})
