function htmlToNode(html) {
    const template = document.createElement('template');
    template.innerHTML = html;
    const nNodes = template.content.childNodes.length;
    if (nNodes !== 1) {
        throw new Error(
            `html parameter must represent a single node; got ${nNodes}. ` +
            'Note that leading or trailing spaces around an element in your ' +
            'HTML, like " <img/> ", get parsed as text nodes neighbouring ' +
            'the element; call .trim() on your input to avoid this.'
        );
    }
    return template.content.firstChild;
}

class BadgeCell {
    constructor(templateHtml, item, progress, isTarget) {
        this.elt = htmlToNode(templateHtml
            .replace("badge.jpg", item.badge + "_512.jpg")
            .replace("maybeTarget", isTarget ? "target" : "")
        );
        this.item = item;
        this.progress = progress;
        this.aElt = this.elt.querySelector('a');
        this.progressElt = this.elt.querySelector('.cell-progress');
        this.broomElt = this.elt.querySelector('.broom');
        this.lockElt = this.elt.querySelector('.lock');
        this.isTarget = isTarget;
        this.elt.querySelector('img').style.transition = 'none';

        if (progress) {
            this.aElt.onclick = (e) => {
                e.preventDefault();
                openPopup(item.badge, progress);
            };
        }

        if (item.badge === 'c0') {
            if (isTarget) {
                this.setGrumpyCatInactive();
            } else if (item.active) {
                this.setGrumpyCatActive();
            } else {
                this.setGrumpyCatInactive();
            }
        } else {
            if (isTarget) {
                this.setAchievementTarget();
            } else if (item.active) {
                this.setAchievementActive();
            } else if (progress) {
                this.setAchievementInactiveInProgress();
            } else {
                this.setAchievementInactiveLocked();
            }
        }
    }

    getElt() {
        return this.elt;
    }

    setAchievementActive() {
        this.elt.classList.add('active');
        this.elt.style.opacity = 1;
    }

    setAchievementTarget() {
        this.elt.classList.remove('active');
        this.lockElt.style.display = 'none';
        this.progressElt.style.display = 'none';
        this.aElt.style.display = 'none';
    }

    setAchievementInactiveLocked() {
        this.elt.classList.remove('active');
        this.lockElt.style.display = 'block';
        this.progressElt.style.display = 'none';
        this.aElt.style.display = 'none';
    }

    setAchievementActiveDisabled() {
        this.elt.classList.add('active');
        this.elt.style.opacity = 0.75;
        this.lockElt.style.display = 'none';
        this.progressElt.style.display = 'none';
        this.aElt.style.display = 'none';
    }

    setAchievementInactiveInProgress() {
        this.elt.classList.remove('active');
        this.lockElt.style.display = 'none';
        this.progressElt.style.display = 'block';
        this.aElt.style.display = 'flex';
        this.progressElt.style.width = this.progress.progress_pct + '%';
        if (this.progress.progress_pct < 33) {
            this.progressElt.classList.add('red');
        } else if (this.progress.progress_pct < 66) {
            this.progressElt.classList.add('yellow');
        } else {
            this.progressElt.classList.add('green');
        }
    }

    setGrumpyCatActive() {
        this.elt.classList.add('active');
        this.broomElt.querySelector('img').style.clipPath = "polygon(0% 0%, " + this.progress.progress_pct + "% 0%, " + this.progress.progress_pct + "% 100%, 0% 100%)"
    }

    setGrumpyCatInactive() {
        this.elt.classList.remove('active');
    }
}


class Board {
    constructor(boardElt, newBadge) {
        this.boardElt = boardElt;
        this.boardEltWrapper = boardElt.querySelector('.boardWrapper');
        this.newBadge = newBadge;

        this.INACTIVE_BADGE_TEMPLATE_ELT = this.boardEltWrapper.getElementsByTagName('div')[0].outerHTML.replace("t0_512.jpg", "badge.jpg");
        this.INACTIVE_UNHAPPY_CAT_TEMPLATE_ELT = this.boardEltWrapper.getElementsByTagName('div')[2].outerHTML.replace("c0_512.jpg", "badge.jpg");

        this.boardEltWrapper.innerHTML = '';

        this.projectileElt = boardElt.querySelector('.projectile');
        this.placeholderElt = boardElt.querySelector('.placeholder');
        this.projectileElt.classList.add('hidden');

        if (newBadge) {
            this.projectileElt.src = '../badge-images/' + newBadge + '_512.jpg';
            this.placeholderElt.src = '../badge-images/' + newBadge + '_512.jpg';
        } else {
            this.projectileElt.style.display = 'none';
            this.placeholderElt.style.display = 'none';
        }

        if (!Board.prototype.registry) {
            Board.prototype.registry = {};
        }

        this.cells = [];
    }

    setHeader(header) {
        this.boardElt.querySelector('h1').innerHTML = header;
    }

    isNewGrumpyCat() {
        return this.newBadge === 'c0';
    }

    addCell(item, progress) {
        const cell = new BadgeCell(item.badge === 'c0'
            ? this.INACTIVE_UNHAPPY_CAT_TEMPLATE_ELT
            : this.INACTIVE_BADGE_TEMPLATE_ELT,
            item, progress, item.last_modified && item.badge === this.newBadge
        );
        this.cells.push(cell);
        this.boardEltWrapper.appendChild(cell.getElt());
    }

    finishAdding() {
        const hasActiveGrumpyCat = this.cells.some(cell => cell.item.badge === 'c0' && cell.item.active);
        if (hasActiveGrumpyCat) {
            this.cells.forEach((cell) => {
                if (cell.item.badge !== 'c0') {
                    if (cell.item.active) {
                        cell.setAchievementActiveDisabled();
                    } else {
                        cell.setAchievementInactiveLocked();
                    }
                }
            });
        }
    }

    waitTillReady() {
        return waitImagesLoadedPromise(this.boardElt.querySelectorAll('img')).then(() => {
            // Need for animation, otherwise it will just jump straight to size of the cell image
            this.projectileElt.style.width = this.projectileElt.width + "px";
            this.placeholderElt.style.width = this.placeholderElt.width + "px";
        });
    }

    move(onDone) {
        const boardCellImgWidth = this.boardElt.querySelector('.board-cell img').width;

        this.projectileElt.style.width = boardCellImgWidth + "px";
        this.placeholderElt.style.width = boardCellImgWidth + "px";

        this.placeholderElt.style.visibility = 'hidden';

        const actionCallback = () => {
            const targetCell = this.cells.find(cell => cell.isTarget);
            if (!targetCell) {
                // Because projectile has nowhere to go
                setTimeout(() => {
                    this.showActionButton();
                    onDone();
                }, 250);
                return;
            }

            const targetRect = targetCell.getElt().getBoundingClientRect();
            const targetX = targetRect.left + window.scrollX;
            const targetY = targetRect.top + window.scrollY;

            const placeholderRect = this.placeholderElt.getBoundingClientRect();
            const placeholderX = placeholderRect.left + window.scrollX;
            const placeholderY = placeholderRect.top + window.scrollY;

            this.projectileElt.style.left = placeholderX + 'px';
            this.projectileElt.style.top = placeholderY + 'px';

            this.placeholderElt.style.width = '0px';

            setTimeout(() => {
                this.projectileElt.style.left = targetX + "px";
                this.projectileElt.style.top = (targetY - boardCellImgWidth) + "px";

                window.addEventListener('transitionend', () => {
                    targetCell.setAchievementActive();
                    this.projectileElt.style.display = 'none';
                    setTimeout(() => {
                        this.showActionButton();
                        onDone();
                    }, 250);
                }, {once: true});
            }, 0);
        };

        if (this.newBadge) {
            window.addEventListener('transitionend', actionCallback, {once: true});
        } else {
            actionCallback();
        }

    }

    newBoardMode() {
        this.placeholderElt.style.display = 'none';
        this.projectileElt.style.display = 'none';
    }

    setActionButton(text, onClick) {
        this.boardElt.querySelector('.action-btn').textContent = text;
        this.boardElt.querySelector('.action-btn').onclick = onClick;
    }

    showActionButton() {
        this.boardElt.querySelector('.action-btn').style.display = 'block';
    }
}