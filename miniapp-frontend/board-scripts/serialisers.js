/**
 * Telegram has a limited number of characters that can be used in URL query parameters. That's why
 * we need to serialize the board and progress map into a single string as short as possible.
 */

function serializeBoard(board) {
    return board.map(item => {
        let ret = "";
        ret += item.badge;
        if (item.active) {
            ret += "a";
        }
        if (item.last_modified) {
            ret += "m";
        }
        return ret;
    }).join("_");
}

function deserializeBoard(itemsStr) {
    return itemsStr.split("_").reduce((acc, chunk) => {
        acc.push({
            badge: chunk.substring(0, 2),
            active: chunk.substring(2).includes('a'),
            last_modified: chunk.substring(2).includes('m')
        });
        return acc;
    }, []);
}

const badgeProgressKey= {
    'c1': "remaining_time_secs",
    'c2': "remaining_time_secs",
    'f0': "remaining_time_secs",
    't0': "remaining_time_secs",
    's0': "remaining_reviews",
    's1': "remaining_reviews",
    's2': "remaining_reviews"
};


function serializeProgressMap(progressMap) {
    const badges = Object.keys(badgeProgressKey);
    return badges.map((badge) => {
        const progressItems = progressMap[badge];
        let ret = badge + "_" + progressItems.length;
        progressItems.forEach(progressItem => {
            ret += "_" + progressItem[badgeProgressKey[badge]];
            ret += "_" + progressItem['progress_pct'];
        });
        return ret;
    }).join("--");
}

function deserializeProgressMap(str) {
    const ret = {};
    str.split("--").forEach((chunk, chunkIdx) =>  {
        const [badge, ...progressItems] = chunk.split("_");
        const items = [];
        ret[badge] = {
            [badgeProgressKey[badge]]: parseInt(progressItems[0]),
            progress_pct: parseInt(progressItems[1])
        };
    });
    return ret;
}