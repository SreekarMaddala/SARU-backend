from collections import Counter


def count_topics(df):
    topic_counts = Counter([t for topics in df['topics'].dropna() for t in topics.split(',')])
    return dict(topic_counts)

