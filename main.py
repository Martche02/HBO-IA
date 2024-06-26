# a ideia inicial é criar uma rede neural categórica sem camadas ocultas
# (que interprete o valor como uma categoria, e não um vetor ou um número) 
# que consiga pegar as classificações das colunas abaixo e gerar a informação
# do tempo, dado por L-K (coluna)
# (cd_multi_empresa[categorica], tp_atendimento[categorica], cd_ori_ate[categorica], ds_especialid[categorica], cd_paciente[categorica], dia_semana[categorica], turno_atendimento[categorica]) -> (tempo_total[numérica em minutos])
import pandas as pd
def dh_atendimento2hora_atendimento():
    # Leitura do arquivo CSV
    df = pd.read_csv('Fluxo atendimentos - pivot SQLT0013.csv')

    # Conversão da coluna dh_atendimento para datetime
    df['dh_atendimento'] = pd.to_datetime(df['dh_atendimento'], format='%d.%m.%Y %H:%M:%S')

    # Aplicação da função de arredondamento e criação da nova coluna hora_atendimento
    df['hora_atendimento'] = df['dh_atendimento'].apply(lambda dt: dt.replace(minute=0, second=0, microsecond=0)).dt.strftime('%H:%M')

    # Salvando o novo dataframe em um arquivo CSV
    df.to_csv('Fluxo atendimentos - pivot SQLT0013.csv', index=False)

    # Exibição do resultado
    print(df.head())
def calcular_tempo_total(df, coluna_inicio, coluna_fim, nova_coluna):
    
    # Criação da nova coluna tempo_total
    df[nova_coluna] = (pd.to_datetime(df[coluna_fim], format='%d.%m.%Y %H:%M:%S') - pd.to_datetime(df[coluna_inicio], format='%Y-%m-%d %H:%M:%S')).dt.total_seconds() // 60
    
    return df
def adicionar_tempo_total():
    df = pd.read_csv('Fluxo atendimentos - pivot SQLT0013.csv')

    # Chamada da função para adicionar a coluna tempo_total
    df = calcular_tempo_total(df, 'dh_atendimento', 'dh_alta', 'tempo_total')

    # Salvando o novo dataframe em um arquivo CSV
    df.to_csv('Fluxo atendimentos - pivot SQLT0013.csv', index=False)

def adicionar_dia_semana(coluna_data='dh_atendimento', nova_coluna='dia_semana'):
    df = pd.read_csv('Fluxo atendimentos - pivot SQLT0013.csv')
    # Conversão da coluna para datetime com o formato correto
    df[coluna_data] = pd.to_datetime(df[coluna_data], format='%Y-%m-%d %H:%M:%S', errors='coerce')
    
    # Adição da nova coluna com o dia da semana
    df[nova_coluna] = df[coluna_data].dt.day_name()
        
    # Salvando o novo dataframe em um arquivo CSV
    df.to_csv('Fluxo atendimentos - pivot SQLT0013.csv', index=False)
def definir_turno(hora):
    if hora >= pd.Timestamp("07:00").time() and hora < pd.Timestamp("13:00").time():
        return "Manha"
    elif hora >= pd.Timestamp("13:00").time() and hora < pd.Timestamp("19:00").time():
        return "Tarde"
    elif hora >= pd.Timestamp("19:00").time() and hora <= pd.Timestamp("22:00").time():
        return "Noite"
    else:
        return "Madrugada"

def adicionar_turno(coluna_hora='hora_atendimento', nova_coluna='turno'):
    # Leitura do arquivo CSV
    df = pd.read_csv('Fluxo atendimentos - pivot SQLT0013.csv')
    # Aplicação da função definir_turno para criar a nova coluna
    df[nova_coluna] =  pd.to_datetime(df[coluna_hora], format='%H:%M').dt.time.apply(definir_turno)
    # Salvando o novo dataframe em um arquivo CSV
    df.to_csv('Fluxo atendimentos - pivot SQLT0013.csv', index=False)

def treinarModeloUni():
    import tensorflow as tf
    from sklearn.model_selection import train_test_split
    from sklearn.preprocessing import OrdinalEncoder, StandardScaler
    import numpy as np

    # Carregar dados
    file_path = 'Fluxo atendimentos - pivot SQLT0013.csv'  # Substitua pelo caminho do seu arquivo CSV
    data = pd.read_csv(file_path)

    # Selecionar colunas categóricas e a coluna de saída
    categorical_columns = ['cd_multi_empresa', 'tp_atendimento', 'cd_ori_ate', 'ds_especialid', 'cd_paciente', 'dia_semana', 'turno']
    target_column = 'tempo_total'

    # Verificar se há NaNs nos dados
    #print(data.isna().sum())

    # Remover ou imputar NaNs
    #data.dropna(inplace=True)  # Simplesmente removendo para este exemplo

    # Verificar e remover NaNs nas colunas relevantes
    data = data.dropna(subset=categorical_columns+[target_column])
    # Separar as características e o alvo
    #print(len(data))
    X = data[categorical_columns]
    y = data[target_column]
    # Transformar colunas categóricas em inteiros
    encoder = OrdinalEncoder()
    X_encoded = encoder.fit_transform(X)

    # Converter para inteiros
    X_encoded = X_encoded.astype(np.int32)

    # Normalizar as características
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X_encoded)
    #print(len(X_scaled))

    # Dividir os dados em treino e teste
    X_train, X_test, y_train, y_test = train_test_split(X_scaled, y, test_size=0.2, random_state=42)

    # Definir o modelo
    # Verificar o tamanho dos dados de treinamento e teste
    #print(f'Tamanho do conjunto de treinamento: {len(X_train)}')
    model = tf.keras.Sequential([
        tf.keras.layers.Dense(1, input_shape=(X_train.shape[1],), activation='linear')
    ])

    # Compilar o modelo
    model.compile(optimizer='adam', loss='mean_squared_error', metrics=['mean_absolute_error'])

    # Treinar o modelo
    history = model.fit(X_train, y_train, epochs=20, batch_size=1, validation_split=0.2)

    # Avaliar o modelo
    loss, mae = model.evaluate(X_test, y_test)
    print(f'Mean Absolute Error on test set: {mae}')

    # Prever
    predictions = model.predict(X_test)
    print(predictions[:10])  # Imprimir as primeiras 10 previsões

    # Salvar o modelo
    model.save('treinarModeloUni.h5')
    model.save_weights('meus_pesos.h5')


    # Plotar a perda durante o treinamento
    import matplotlib.pyplot as plt

    plt.plot(history.history['loss'], label='loss')
    plt.plot(history.history['val_loss'], label='val_loss')
    plt.xlabel('Epoch')
    plt.ylabel('Loss')
    plt.legend()
    plt.show()
# treinarModeloUni()
# import pandas as pd
# import tensorflow as tf
# from sklearn.model_selection import train_test_split
# from sklearn.preprocessing import OrdinalEncoder, StandardScaler, LabelEncoder
# import numpy as np
# import itertools
# import matplotlib.pyplot as plt

def treinarModeloDuo():
    # Carregar dados
    file_path = 'Fluxo atendimentos - pivot SQLT0013.csv'  # Substitua pelo caminho do seu arquivo CSV
    data = pd.read_csv(file_path)

    # Selecionar colunas categóricas e a coluna de saída
    categorical_columns = ['cd_multi_empresa', 'tp_atendimento', 'cd_ori_ate', 'ds_especialid', 'cd_paciente', 'dia_semana', 'turno']
    target_column = 'tempo_total'

    # Verificar e remover NaNs nas colunas relevantes
    data = data.dropna(subset=categorical_columns + [target_column])
    
    # Criar novas colunas combinando pares de colunas categóricas
    for col1, col2 in itertools.combinations(categorical_columns, 2):
        new_col_name = f'{col1}_{col2}'
        data[new_col_name] = data[col1].astype(str) + '_' + data[col2].astype(str)
    
    # Atualizar a lista de colunas categóricas para incluir as novas colunas
    new_categorical_columns = [f'{col1}_{col2}' for col1, col2 in itertools.combinations(categorical_columns, 2)]
    
    # Separar as características e o alvo
    X = data[new_categorical_columns]
    y = data[target_column]

    # Transformar colunas categóricas em índices numéricos usando LabelEncoder
    for col in new_categorical_columns:
        le = LabelEncoder()
        X[col] = le.fit_transform(X[col])

    # Normalizar as características do alvo
    scaler = StandardScaler()
    y_scaled = scaler.fit_transform(y.values.reshape(-1, 1))

    # Definir os inputs para os embeddings
    inputs = []
    embeddings = []
    for col in new_categorical_columns:
        input_col = tf.keras.Input(shape=(1,), name=col)
        unique_values = X[col].nunique()
        embedding_col = tf.keras.layers.Embedding(input_dim=unique_values + 1, output_dim=min(50, unique_values // 2))(input_col)
        flattened_col = tf.keras.layers.Flatten()(embedding_col)
        inputs.append(input_col)
        embeddings.append(flattened_col)

    concatenated = tf.keras.layers.Concatenate()(embeddings)

    # Definir o modelo
    x = tf.keras.layers.Dense(64, activation='relu')(concatenated)
    x = tf.keras.layers.Dense(32, activation='relu')(x)
    output = tf.keras.layers.Dense(1, activation='linear')(x)
    model = tf.keras.Model(inputs=inputs, outputs=output)

    # Compilar o modelo
    model.compile(optimizer='adam', loss='mean_squared_error', metrics=['mean_absolute_error'])

    # Dividir os dados em treino e teste
    X_train, X_test, y_train, y_test = train_test_split(X, y_scaled, test_size=0.2, random_state=42)

    # Preparar os inputs para o treinamento
    train_inputs = {col: np.array(X_train[col]) for col in new_categorical_columns}
    test_inputs = {col: np.array(X_test[col]) for col in new_categorical_columns}

    # Treinar o modelo
    history = model.fit(train_inputs, y_train, epochs=10, batch_size=64, validation_split=0.2)

    # Avaliar o modelo
    loss, mae = model.evaluate(test_inputs, y_test)
    print(f'Mean Absolute Error on test set: {mae}')

    # Prever
    predictions = model.predict(test_inputs)
    print(predictions[:10])  # Imprimir as primeiras 10 previsões

    # Salvar o modelo
    model.save('treinarModeloDuo.h5')
    model.save_weights('meus_pesos_duo.h5')

    # Plotar a perda durante o treinamento
    plt.plot(history.history['loss'], label='loss')
    plt.plot(history.history['val_loss'], label='val_loss')
    plt.xlabel('Epoch')
    plt.ylabel('Loss')
    plt.legend()
    plt.show()

# Executar a função
# treinarModeloDuo()
def novatentativa():
    import pandas as pd

    # Carregar os dados
    file_path = 'Fluxo atendimentos - pivot SQLT0013.csv'
    df = pd.read_csv(file_path)

    # Selecionar as colunas relevantes
    selected_columns = [
        'cd_multi_empresa', 'tp_atendimento', 'cd_ori_ate', 
        'ds_especialid', 'dia_semana', 'turno', 'tempo_total'
    ]
    df_relevant = df[selected_columns]

    # Função para reduzir categorias menos frequentes
    def reduce_categories(df, column, top_n=10):
        top_categories = df[column].value_counts().nlargest(top_n).index
        df[column] = df[column].apply(lambda x: x if x in top_categories else 'Outros')
        return df

    # Reduzir as categorias menos frequentes nas variáveis selecionadas
    for col in selected_columns[:-1]:  # exceto 'tempo_total'
        df_relevant = reduce_categories(df_relevant, col)

    # Agrupar os dados por combinações de categorias e calcular a média do tempo total
    grouped_df = df_relevant.groupby(selected_columns[:-1]).agg({'tempo_total': 'mean'}).reset_index()

    # Ordenar as combinações pela média do tempo total
    sorted_grouped_df = grouped_df.sort_values(by='tempo_total', ascending=False)

    # Mostrar os resultados
    print(sorted_grouped_df.head(20))
novatentativa()