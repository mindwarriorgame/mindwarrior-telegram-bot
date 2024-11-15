from badges_manager import BoardCell

def serialize_cell(cell: BoardCell) -> str:
    ret = cell["badge"]
    if cell.get("is_active"):
        ret += "a"
    if cell.get("is_last_modified"):
        ret += "m"
    return ret

badgeProgressKey = {
    'c1': "remaining_time_secs",
    'c2': "remaining_time_secs",
    'f0': "remaining_time_secs",
    't0': "remaining_time_secs",
    's0': "remaining_reviews",
    's1': "remaining_reviews",
    's2': "remaining_reviews",
    'c0': "remaining_reviews",
};

def serialize_progress(progress: dict) -> str:
    serialized_items = []
    for badge, item in progress.items():
        chunk = badge
        chunk += "_" + str(item[badgeProgressKey[badge]]) + "_" + str(item["progress_pct"])
        if item.get("progress_pct_delta"):
            chunk += "_" + str(item["progress_pct_delta"])
        else:
            chunk += "_0"
        serialized_items.append(chunk)
    return "--".join(serialized_items)

def serialize_board(board: [BoardCell]) -> str:
    return "_".join([serialize_cell(cell) for cell in board])
