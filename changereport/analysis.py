"""Data aggregation and statistics for change report."""

import pandas as pd


def compute_all_analysis(df: pd.DataFrame) -> dict:
    """Compute all analysis results and return as a dictionary."""
    return {
        "total_changes": len(df),
        "by_category": changes_by_category(df),
        "by_type": changes_by_type(df),
        "by_impact": changes_by_impact(df),
        "implementer_workload": implementer_workload(df),
        "timeline": timeline_distribution(df),
        "hourly": hourly_distribution(df),
        "weekly": weekly_distribution(df),
        "avg_duration_by_category": average_duration_by_category(df),
        "high_impact": high_impact_changes(df),
        "date_range": date_range(df),
        "busiest_day": busiest_day(df),
        "busiest_category": busiest_category(df),
        "regions": regions_summary(df),
    }


def changes_by_category(df: pd.DataFrame) -> pd.Series:
    """Count changes per category."""
    if "category" not in df.columns:
        return pd.Series(dtype=int)
    return df["category"].value_counts().sort_values(ascending=False)


def changes_by_type(df: pd.DataFrame) -> pd.Series:
    """Count changes per type."""
    if "type_of_change" not in df.columns:
        return pd.Series(dtype=int)
    return df["type_of_change"].value_counts()


def changes_by_impact(df: pd.DataFrame) -> pd.Series:
    """Count changes per impact level."""
    if "impact_description" not in df.columns:
        return pd.Series(dtype=int)
    return df["impact_description"].value_counts()


def implementer_workload(df: pd.DataFrame) -> pd.DataFrame:
    """Group by customer_name, count changes and sum duration."""
    if "customer_name" not in df.columns:
        return pd.DataFrame()

    work_df = df[df["customer_name"].str.strip() != ""].copy()
    if work_df.empty:
        return pd.DataFrame()

    # Convert duration to numeric for aggregation
    work_df["dur_numeric"] = pd.to_numeric(work_df["duration_hours"], errors="coerce")

    grouped = work_df.groupby("customer_name").agg(
        change_count=("id", "count"),
        total_hours=("dur_numeric", "sum"),
        categories=("category", lambda x: ", ".join(sorted(str(v) for v in x.unique() if pd.notna(v) and str(v).strip()))),
    ).sort_values("change_count", ascending=False)

    grouped["total_hours"] = grouped["total_hours"].round(1)
    return grouped


def timeline_distribution(df: pd.DataFrame) -> pd.Series:
    """Changes per calendar date."""
    valid = df[df["start_datetime"].notna()]
    if valid.empty:
        return pd.Series(dtype=int)
    return valid["start_datetime"].dt.date.value_counts().sort_index()


def hourly_distribution(df: pd.DataFrame) -> pd.Series:
    """Changes by hour of day."""
    valid = df[df["start_datetime"].notna()]
    if valid.empty:
        return pd.Series(dtype=int)
    counts = valid["start_datetime"].dt.hour.value_counts().sort_index()
    # Fill missing hours with 0 for a complete chart
    all_hours = pd.Series(0, index=range(24))
    all_hours.update(counts)
    return all_hours


def weekly_distribution(df: pd.DataFrame) -> pd.Series:
    """Changes by day of week."""
    valid = df[df["start_datetime"].notna()]
    if valid.empty:
        return pd.Series(dtype=int)
    day_order = ["Monday", "Tuesday", "Wednesday", "Thursday",
                 "Friday", "Saturday", "Sunday"]
    counts = valid["start_datetime"].dt.day_name().value_counts()
    return counts.reindex(day_order, fill_value=0)


def average_duration_by_category(df: pd.DataFrame) -> pd.Series:
    """Average change duration by category."""
    valid = df[df["duration_hours"].notna()].copy()
    if valid.empty:
        return pd.Series(dtype=float)
    valid["dur_numeric"] = pd.to_numeric(valid["duration_hours"], errors="coerce")
    return valid.groupby("category")["dur_numeric"].mean().round(2)


def high_impact_changes(df: pd.DataFrame) -> pd.DataFrame:
    """Filter to only impactful changes (not 'No Impact')."""
    if "impact_description" not in df.columns:
        return pd.DataFrame()
    return df[df["impact_description"].str.strip() != "No Impact"]


def date_range(df: pd.DataFrame) -> tuple:
    """Return (earliest_date, latest_date) from the data."""
    valid = df[df["start_datetime"].notna()]
    if valid.empty:
        return (None, None)
    return (
        valid["start_datetime"].min().date(),
        valid["start_datetime"].max().date(),
    )


def busiest_day(df: pd.DataFrame) -> str:
    """Return the date with the most changes."""
    timeline = timeline_distribution(df)
    if timeline.empty:
        return "N/A"
    top = timeline.idxmax()
    return f"{top} ({timeline.max()} changes)"


def busiest_category(df: pd.DataFrame) -> str:
    """Return the category with the most changes."""
    cats = changes_by_category(df)
    if cats.empty:
        return "N/A"
    return f"{cats.index[0]} ({cats.iloc[0]} changes)"


def regions_summary(df: pd.DataFrame) -> pd.Series:
    """Count changes per region (exploding comma-separated regions)."""
    if "regions_affected" not in df.columns:
        return pd.Series(dtype=int)

    all_regions = []
    for val in df["regions_affected"]:
        val = str(val).strip()
        if val and val not in ("", "N/A", "n/a", "0", "none", "None"):
            parts = [r.strip() for r in val.split(",") if r.strip()]
            all_regions.extend(parts)

    if not all_regions:
        return pd.Series(dtype=int)
    return pd.Series(all_regions).value_counts()
