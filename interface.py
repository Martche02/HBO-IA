import pandas as pd

# Função para reduzir categorias menos frequentes
def reduce_categories(df, column, top_n=10):
    top_categories = df[column].value_counts().nlargest(top_n).index
    df[column] = df[column].apply(lambda x: x if x in top_categories else 'Outros')
    return df

# Carregar os dados
file_path = 'Fluxo atendimentos - pivot SQLT0013.csv'
df = pd.read_csv(file_path)

# Selecionar as colunas relevantes
all_columns = ['cd_multi_empresa', 'tp_atendimento', 'cd_ori_ate', 'ds_especialid', 'dia_semana', 'turno']

# Solicitar ao usuário as variáveis para análise
print("Selecione as variáveis para análise (escolha entre: cd_multi_empresa, tp_atendimento, cd_ori_ate, ds_especialid, dia_semana, turno):")
selected_columns = input("Digite as variáveis separadas por vírgula: ").replace(" ", "").split(",")

if selected_columns:
    selected_columns = [col for col in selected_columns if col in all_columns]
    selected_columns.append('tempo_total')
    df_relevant = df[selected_columns]

    # Reduzir as categorias menos frequentes nas variáveis selecionadas
    for col in selected_columns[:-1]:  # exceto 'tempo_total'
        df_relevant = reduce_categories(df_relevant, col)

    # Agrupar os dados por combinações de categorias, calcular a média do tempo total e contar os casos
    grouped_df = df_relevant.groupby(selected_columns[:-1]).agg(
        tempo_total_mean=('tempo_total', 'mean'),
        casos=('tempo_total', 'size')
    ).reset_index()

    # Ordenar as combinações pela média do tempo total
    sorted_grouped_df = grouped_df.sort_values(by='tempo_total_mean', ascending=False)

    # Mostrar os resultados
    print("\nCombinations Impacting Total Time (Top 20):")
    print(sorted_grouped_df.head(20))
else:
    print("Nenhuma variável selecionada.")
