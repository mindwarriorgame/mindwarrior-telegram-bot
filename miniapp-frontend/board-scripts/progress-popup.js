// https://stackoverflow.com/a/26514148/1432640
const Base64={_keyStr:"ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/=",encode:function(e){var t="";var n,r,i,s,o,u,a;var f=0;e=Base64._utf8_encode(e);while(f<e.length){n=e.charCodeAt(f++);r=e.charCodeAt(f++);i=e.charCodeAt(f++);s=n>>2;o=(n&3)<<4|r>>4;u=(r&15)<<2|i>>6;a=i&63;if(isNaN(r)){u=a=64}else if(isNaN(i)){a=64}t=t+this._keyStr.charAt(s)+this._keyStr.charAt(o)+this._keyStr.charAt(u)+this._keyStr.charAt(a)}return t},decode:function(e){var t="";var n,r,i;var s,o,u,a;var f=0;e=e.replace(/[^A-Za-z0-9\+\/\=]/g,"");while(f<e.length){s=this._keyStr.indexOf(e.charAt(f++));o=this._keyStr.indexOf(e.charAt(f++));u=this._keyStr.indexOf(e.charAt(f++));a=this._keyStr.indexOf(e.charAt(f++));n=s<<2|o>>4;r=(o&15)<<4|u>>2;i=(u&3)<<6|a;t=t+String.fromCharCode(n);if(u!=64){t=t+String.fromCharCode(r)}if(a!=64){t=t+String.fromCharCode(i)}}t=Base64._utf8_decode(t);return t},_utf8_encode:function(e){e=e.replace(/\r\n/g,"\n");var t="";for(var n=0;n<e.length;n++){var r=e.charCodeAt(n);if(r<128){t+=String.fromCharCode(r)}else if(r>127&&r<2048){t+=String.fromCharCode(r>>6|192);t+=String.fromCharCode(r&63|128)}else{t+=String.fromCharCode(r>>12|224);t+=String.fromCharCode(r>>6&63|128);t+=String.fromCharCode(r&63|128)}}return t},_utf8_decode:function(e){var t="";var n=0;var r=c1=c2=0;while(n<e.length){r=e.charCodeAt(n);if(r<128){t+=String.fromCharCode(r);n++}else if(r>191&&r<224){c2=e.charCodeAt(n+1);t+=String.fromCharCode((r&31)<<6|c2&63);n+=2}else{c2=e.charCodeAt(n+1);c3=e.charCodeAt(n+2);t+=String.fromCharCode((r&15)<<12|(c2&63)<<6|c3&63);n+=3}}return t}}


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
    const actions = JSON.parse(Base64.decode(actionsBase64 || Base64.encode('{}')));
    let content = `<img src="../badge-images/${badge}_512.jpg" />`;
    if (badge === 'c0') {
        content += `<p>Earn any badge to kick it out!</p>`;
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
        content += `<p>Update the <i>Formula</i> after ${toTimeInterval(action.remaining_time_secs)} 🧪</p>`;
        content += renderProgressBar(action.progress_pct);
    } else if (badge === 't0') {
        let action = actions[0];
        content += `<p>Play the game during next ${toTimeInterval(action.remaining_time_secs)} 🎮</p>`;
        content += renderProgressBar(action.progress_pct);
    } else if (badge === 's0' || badge === 's1' || badge === 's2') {
        let action = actions[0];
        content += `<p>Review <i>Formula</i> ${action.remaining_reviews} more time(s) without misses 🚫🟥</p>`;
        content += renderProgressBar(action.progress_pct);
    }

    content += "<p><button class='action-btn' onclick='closePopup()'>Close</button></p>";

    document.getElementById('popup').innerHTML = content;

    document.getElementById('popup').classList.add('show');
    document.getElementById('overlay').classList.add('show');
}

function closePopup() {
    document.getElementById('popup').classList.remove('show');
    document.getElementById('overlay').classList.remove('show');
}