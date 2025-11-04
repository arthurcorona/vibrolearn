import sys
import os
import numpy as np

project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, project_root)

# 
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score

from dataset.cwru.utils import get_code_from_faulty_bearing, get_list_of_folds_rauber_loca_et_al
from dataset import utils 

RAW_DIR_PATH = 'raw_data' 
CHANNEL = 'DE_time' 
SEGMENT_LENGTH = 2048 #segmento tem que ser do mesmo tamanho que do utils.py


def run_experiments(faulty_bearing='Drive End', sample_rate='12000'):
    folds = get_list_of_folds_rauber_loca_et_al(faulty_bearing, sample_rate)
    R = 8  # rounds
    K = 4  # folds em cada round
    all_accuracies = []

    for round_id in range(R):
        print(f"\n=== ROUND {round_id + 1} ===")
        round_accuracies = []

        for fold_id in range(K):
            print(f"\n--- Fold {fold_id + 1} (Test fold) ---")

            # test e fold
            test_metadata_list = folds[fold_id]
            train_folds_metadata = [f for i, f in enumerate(folds) if i != fold_id]
           
            train_metadata_list = [sample for fold in train_folds_metadata for sample in fold]

            np.random.shuffle(train_metadata_list)
            np.random.shuffle(test_metadata_list)

            print(f"Carregando {len(train_metadata_list)} registros de treino...")
            X_train_raw, y_train = utils.get_X_y(
                train_metadata_list, 
                raw_dir_path=RAW_DIR_PATH, 
                channel=CHANNEL, 
                segment_length=SEGMENT_LENGTH
            )

            print(f"Carregando {len(test_metadata_list)} registros de teste...")
            X_test_raw, y_test = utils.get_X_y(
                test_metadata_list, 
                raw_dir_path=RAW_DIR_PATH, 
                channel=CHANNEL, 
                segment_length=SEGMENT_LENGTH
            )
            
            print(f"Dados carregados: {X_train_raw.shape[0]} segmentos de treino, {X_test_raw.shape[0]} segmentos de teste.")


            #necessário tornar o dado de 3D para 2D (amostra, tamanho de segmento e 1 em amostras e features)
            n_samples_train = X_train_raw.shape[0]
            X_train = X_train_raw.reshape((n_samples_train, -1)) #(N, 2048, 1) em (N, 2048)

            n_samples_test = X_test_raw.shape[0]
            X_test = X_test_raw.reshape((n_samples_test, -1)) # Transforma (N, 2048, 1) em (N, 2048)

            print("Treinando o modelo RandomForestClassifier...")
            model = RandomForestClassifier(n_estimators=100, random_state=round_id)
            model.fit(X_train, y_train)

            print("Testando o modelo...")
            y_pred = model.predict(X_test)
            acc = accuracy_score(y_test, y_pred)
            print(f"Accuracy: {acc:.4f}")

            round_accuracies.append(acc)

        # acuracia
        mean_acc = np.mean(round_accuracies)
        print(f"\n>>> Mean accuracy (Round {round_id + 1}): {mean_acc:.4f}")
        all_accuracies.append(mean_acc)

    print("\n=== FINAL RESULTS ===")
    print(f"Overall mean accuracy: {np.mean(all_accuracies):.4f}")
    print(f"Std deviation: {np.std(all_accuracies):.4f}")

if __name__ == "__main__":
    print("--- Iniciando os experimentos ---")
    run_experiments() 
    print("--- Experimentos finalizados ---")