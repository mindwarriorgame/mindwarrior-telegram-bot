function toTimeInterval(secs) {
    let hours = Math.floor(secs / 3600);
    let minutes = Math.floor((secs % 3600) / 60);
    return `${hours}${window.lang.hour_one_letter} ${minutes}${window.lang.minute_one_letter}`;
}

function renderProgressBar(pct) {
    return `<div class="progress-container">
            <div class="progress-bar" style="width: ${pct}%;"></div>
            <span class="progress-text">${pct}%</span>
        </div>`;
}

function renderReviewWithoutSomething(template, pct, counter, counterIsTime= true)  {
    const ret = [
        '<p>',
        template.replace('###', counterIsTime ? toTimeInterval(counter) : counter),
        '</p>'
    ];
    ret.push(renderProgressBar(pct));
    return ret.join(' ');
}

function openPopup(badge, progress) {
    let content = `<img src="../badge-images/${badge}_512.jpg" />`;

    const timeBadges = {
        'c1': window.lang.review_without_misses_duration,
        'c2': window.lang.review_without_reminders_duration,
        'f0': window.lang.update_formula_after,
        't0': window.lang.play_game,
    };

    const reviewBadges = {
        's0': window.lang.review_without_misses_times,
        's1': window.lang.review_without_misses_times,
        's2': window.lang.review_without_misses_times
    }

    if (timeBadges[badge]) {
        content += renderReviewWithoutSomething(timeBadges[badge], progress.progress_pct, progress.remaining_time_secs);
    } else if (badge === 'c0') {
        const message = window.lang.review_times
            .replace("##1", Math.ceil(progress.remaining_reviews / 3))
            .replace("##2", Math.ceil(progress.remaining_reviews / 2))
            .replace("##3", progress.remaining_reviews);
        const ret = [
            '<p>',
            message,
            '</p>'
        ];
        ret.push(renderProgressBar(progress.progress_pct || 0));
        content += ret.join(' ');
    } else {
        content += renderReviewWithoutSomething(reviewBadges[badge], progress.progress_pct, progress.remaining_reviews, false);
    }

    content += `<p><button class='action-btn' onclick='closePopup()'>${window.lang.close}</button></p>`;

    document.getElementById('popup').innerHTML = content;

    document.getElementById('popup').classList.add('show');
    document.getElementById('overlay').classList.add('show');
}

function closePopup() {
    document.getElementById('popup').classList.remove('show');
    document.getElementById('overlay').classList.remove('show');
}