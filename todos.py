import pandas as pd
import itertools

# Função para reduzir categorias menos frequentes
def reduce_categories(df, column, top_n=10):
    top_categories = df[column].value_counts().nlargest(top_n).index
    df[column] = df[column].apply(lambda x: x if x in top_categories else 'Outros')
    return df

# Função para analisar os dados
def analyze_data(df, selected_vars):
    # Reduzir categorias
    for col in selected_vars:
        df = reduce_categories(df, col)
    
    # Agrupar os dados por combinações de categorias e calcular a média do tempo total e contagem de casos
    grouped_df = df.groupby(selected_vars).agg(
        tempo_total_mean=('tempo_total', 'mean'),
        casos=('tempo_total', 'size')
    ).reset_index()
    
    return grouped_df

# Carregar os dados
file_path = 'Fluxo atendimentos - pivot SQLT0013.csv'
df = pd.read_csv(file_path)

# Todas as colunas disponíveis para análise
all_columns = ['cd_multi_empresa', 'tp_atendimento', 'cd_ori_ate', 'ds_especialid', 'dia_semana', 'turno']

# Gerar todas as combinações possíveis de variáveis
combinations = []
for i in range(1, len(all_columns) + 1):
    combinations.extend(itertools.combinations(all_columns, i))

# Analisar todas as combinações
all_results = []

for combination in combinations:
    result_df = analyze_data(df.copy(), list(combination))
    result_df['combination'] = result_df.apply(lambda row: ' - '.join([f"{col}: {row[col]}" for col in combination]), axis=1)
    all_results.append(result_df)

# Concatenar todos os resultados
all_results_df = pd.concat(all_results)

# Ordenar as combinações pela média do tempo total e exibir as 20 mais demoradas
sorted_results_df = all_results_df.sort_values(by='tempo_total_mean', ascending=False)

# Exibir os resultados
print("Top 20 combinações mais demoradas:")
print(sorted_results_df[['combination', 'tempo_total_mean', 'casos']].head(20))
