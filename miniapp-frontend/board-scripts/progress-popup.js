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

function renderReviewWithoutSomething(template, step, inactive, pct, timeSecs, withProgressBar)  {
    let stepPrefix = '';
    if (step) {
        stepPrefix = `${step}. `;
    }
    const ret = [
        '<p class="pct' + (inactive ? 100 : 0) + '">',

        (pct == 100) ? '✅ ' : '',
        stepPrefix,

        template.replace('###', toTimeInterval(timeSecs)),
        '</p>'
    ];
    if (withProgressBar) {
        ret.push(renderProgressBar(pct));
    }
    return ret.join(' ');
}

function openPopup(badge, actionsBase64) {
    const actions = JSON.parse(window.Base64.decode(actionsBase64 || window.Base64.encode('{}')));
    let content = `<img src="../badge-images/${badge}_512.jpg" />`;
    if (badge === 'c0') {
        content += `<p>${window.lang.kick_out}</p>`;
    } else if (badge === 'c1') {
        let action = actions[0];
        content += renderReviewWithoutSomething(window.lang.review_without_misses_duration, null, action.progress_pct == 100, action.progress_pct, action.remaining_time_secs, true);
    } else if (badge === 'c2') {
        let action1 = actions[0];
        content += renderReviewWithoutSomething(window.lang.review_without_misses_duration, 1, action1.progress_pct == 100, action1.progress_pct, action1.remaining_time_secs, action1.progress_pct < 100);

        action2 = actions[1];
        content += renderReviewWithoutSomething(window.lang.review_without_reminders_duration, 2, action1.progress_pct < 100, action2.progress_pct, action2.remaining_time_secs, action1.progress_pct == 100 && action2.progress_pct < 100);
    } else if (badge === 'f0') {
        let action = actions[0];
        content += `<p>${window.lang.update_formula_after.replace('###', toTimeInterval(action.remaining_time_secs))}</p>`;
        content += renderProgressBar(action.progress_pct);
    } else if (badge === 't0') {
        let action = actions[0];
        content += `<p>${window.lang.play_game.replace('###', toTimeInterval(action.remaining_time_secs))}</p>`;
        content += renderProgressBar(action.progress_pct);
    } else if (badge === 's0' || badge === 's1' || badge === 's2') {
        let action = actions[0];
        content += `<p>${window.lang.review_without_misses_times.replace('###', action.remaining_reviews)}</p>`;
        content += renderProgressBar(action.progress_pct);
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