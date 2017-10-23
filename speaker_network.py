import pandas as pd
import ast
import networkx as nx
import matplotlib.pyplot as plt
import community
from tabulate import tabulate

b_dir = './ted-talks/'

df = pd.read_csv(b_dir + 'ted_main.csv')
import datetime
df['film_date'] = df['film_date'].apply(
    lambda x: datetime.datetime.fromtimestamp(int(x)).strftime('%d-%m-%Y'))
df['published_date'] = df['published_date'].apply(
    lambda x: datetime.datetime.fromtimestamp(int(x)).strftime('%d-%m-%Y'))


def get_related_df(df, col):
    df['related_talks_eval'] = df['related_talks'].apply(
        lambda x: ast.literal_eval(x))
    s = df.apply(lambda x: pd.Series([dic[col] for dic in x['related_talks_eval']]), axis=1).stack(
    ).reset_index(level=1, drop=True)
    s.name = 'related_%s' % col
    related_df = df.drop('related_talks_eval', axis=1).join(s)
    return related_df


def get_G(main_col, related_col_suffix, speaker_occupation=None):
    related_df = get_related_df(df, related_col_suffix)
    related_col = 'related_%s' % related_col_suffix
    if speaker_occupation is not None:
        related_df = related_df.loc[related_df['speaker_occupation'].fillna(
            '').str.contains(speaker_occupation)]
    related_df = related_df[[main_col, related_col]]
    related_df = related_df.groupby(
        [main_col, related_col]).size().reset_index(name='counts')
    edges = list(
        zip(related_df[main_col], related_df[related_col]))
    G = nx.Graph()
    G.add_edges_from(edges)
    return G


G_speaker_computer = get_G('main_speaker', 'speaker', 'Computer')

plt.figure(figsize=(25, 25))
# with_labels=False
# nx.draw(G_computer)
pos = nx.spring_layout(G_speaker_computer, k=0.15)
nx.draw_networkx(G_speaker_computer, pos, node_size=25, node_color='blue')
# plt.show()
plt.savefig('G_speaker_computer.png', dpi=200)
plt.clf()
plt.cla()
plt.close()


def draw_partition(G, partition):
    plt.figure(figsize=(25, 25))
    size = float(len(set(partition.values())))
    pos = nx.spring_layout(G)
    count = 0.
    for com in set(partition.values()):
        count = count + 1.
        list_nodes = [nodes for nodes in partition.keys()
                      if partition[nodes] == com]
        nx.draw_networkx_nodes(G, pos, list_nodes, node_size=20,
                               node_color=str(count / size))
    nx.draw_networkx_edges(G, pos, alpha=0.5)
    plt.show()


def draw_partition_N(category, G, partition, n):
    plt.figure(figsize=(25, 25))
    list_nodes = [nodes for nodes in partition.keys()
                  if partition[nodes] == n]
    H = G.subgraph(list_nodes)
    pos = nx.spring_layout(H, k=0.15)
    nx.draw_networkx(H, pos, node_size=25, node_color='blue')
    # plt.show()
    plt.savefig('%s_partition_%s.png' % (category, str(n)), dpi=200)
    plt.clf()
    plt.cla()
    plt.close()


G_speaker_all = get_G('main_speaker', 'speaker', None)


# first compute the best partition
partition_speaker = community.best_partition(G_speaker_all)
# drawing


par_speaker_pd = pd.DataFrame.from_dict(partition_speaker, orient='index')
par_speaker_pd.columns = ['partition']
par_speaker_pd.groupby('partition').size().sort_values(ascending=False)

G_title_all = get_G('title', 'title', None)
plt.figure(figsize=(25, 25))
#nx.draw(G_title_all, with_labels=False)

# first compute the best partition
partition_title = community.best_partition(G_title_all)
# drawing


par_title_pd = pd.DataFrame.from_dict(partition_title, orient='index')
par_title_pd.columns = ['partition']
sorted_par_title = par_title_pd.groupby(
    'partition').size().sort_values(ascending=False)
print(tabulate(sorted_par_title.reset_index(), tablefmt="pipe", headers="keys"))
draw_partition_N('title', G_title_all, partition_title, 18)
