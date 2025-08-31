def remove_highly_correlated_columns(df, threshold):
    """
    Removes columns from a DataFrame that have a correlation coefficient above a given threshold.

    Args:
        df (pd.DataFrame): The DataFrame to remove columns from.
        threshold (float): The correlation coefficient threshold.

    Returns:
        pd.DataFrame: The DataFrame with the highly correlated columns removed.
    """

    corr_matrix = df.corr()
    highly_correlated_cols = set()
    for i in range(len(corr_matrix.columns)):
        for j in range(i + 1, len(corr_matrix.columns)):
            if abs(corr_matrix.iloc[i, j]) > threshold:
                colname = (
                    corr_matrix.columns[i]
                    if corr_matrix.iloc[i, j] > 0
                    else corr_matrix.columns[j]
                )
                highly_correlated_cols.add(colname)

    return df.drop(columns=list(highly_correlated_cols))
