from dataset.cwru.rauber_loca_et_al import single_channel_X_y_DE_FE_12k
from dataset.utils import read_registers_from_config, download_files_from_registers
from assesment.crossvalidation import performance
from sklearn.metrics import accuracy_score, f1_score, confusion_matrix
from estimators import rfwfe 


CWRU_CONFIG_PATH = "dataset/cwru/config.csv"
CWRU_RAW_DIR = "raw_data/cwru"
CWRU_BASE_URL = "https://engineering.case.edu/sites/default/files/"

METRICS = [
    accuracy_score,
    lambda y_true, y_pred: f1_score(y_true, y_pred, average="macro"),
    confusion_matrix,
]


def prepare_cwru_data(combination=0, segment_length=2048):
    registers = read_registers_from_config(CWRU_CONFIG_PATH)
    download_files_from_registers(registers, CWRU_RAW_DIR, CWRU_BASE_URL)
    return single_channel_X_y_DE_FE_12k(combination, segment_length)


def run(model, combination=0, segment_length=2048, verbose=False):
    list_of_X_y = prepare_cwru_data(combination, segment_length)
    return performance(model, list_of_X_y, list_of_metrics=METRICS, verbose=verbose)