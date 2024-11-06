class Board {
    constructor(boardElt) {
        this.boardElt = boardElt;
        this.boardEltWrapper = boardElt.querySelector('.boardWrapper');

        this.INACTIVE_BADGE_TEMPLATE_ELT = this.boardEltWrapper.getElementsByTagName('p')[0].outerHTML.replace("t0_512.jpg", "badge.jpg");
        this.ACTIVE_BADGE_TEMPLATE_ELT = this.boardEltWrapper.getElementsByTagName('p')[1].outerHTML.replace("f0_512.jpg", "badge.jpg");
        this.INACTIVE_UNHAPPY_CAT_TEMPLATE_ELT = this.boardEltWrapper.getElementsByTagName('p')[2].outerHTML.replace("c0_512.jpg", "badge.jpg");
        this.ACTIVE_UNHAPPY_CAT_TEMPLATE_ELT = this.boardEltWrapper.getElementsByTagName('p')[3].outerHTML.replace("c0_512.jpg", "badge.jpg");

        this.boardEltWrapper.innerHTML = '';
        this.targetBadge = undefined;

        this.projectileElt = boardElt.querySelector('.projectile');
        this.placeholderElt = boardElt.querySelector('.placeholder');
        this.projectileElt.classList.add('hidden');

        if (!Board.prototype.registry) {
            Board.prototype.registry = {};
        }
    }

    setHeader(header) {
        this.boardElt.querySelector('h1').innerHTML = header;
    }

    isTargetGrumpyCat() {
        return this.targetBadge === 'c0';
    }

    addCell(item, progressItems) {
        let itemHtml = "";
        if (item.active && item.badge === 'c0') {
            itemHtml = this.ACTIVE_UNHAPPY_CAT_TEMPLATE_ELT;
        } else if (item.active) {
            itemHtml = this.ACTIVE_BADGE_TEMPLATE_ELT;
        } else if (item.badge === 'c0') {
            itemHtml = this.INACTIVE_UNHAPPY_CAT_TEMPLATE_ELT;
        } else {
            itemHtml = this.INACTIVE_BADGE_TEMPLATE_ELT;
        }
        itemHtml = itemHtml.replace("badge.jpg", item.badge + "_512.jpg");
        if (item.target) {
            itemHtml = itemHtml.replace("maybeTarget", "target");
            let projectile = item.badge;
            if (item.projectileOverride) {
                projectile = item.projectileOverride;
            }
            this.projectileElt.src = '../badge-images/' + projectile + '_512.jpg';
            this.placeholderElt.src = '../badge-images/' + projectile + '_512.jpg';
            this.targetBadge = item.badge;
            this.projectileElt.classList.remove('hidden');
            if (item.badge !== 'c0') {
                itemHtml = itemHtml.replace('<a', '<a style="display:none;" ');
                itemHtml = itemHtml.replace('width: 100%', 'width: ' + 0 + '%');
            }
        } else if (progressItems) {
            itemHtml = itemHtml.replace('openPopup()', 'openPopup(\'' + item.badge + '\', \'' + window.Base64.encode(JSON.stringify(progressItems)) + '\')');

            let pct = 0;
            for (let actionIdx = 0; actionIdx < progressItems.length; actionIdx++) {
                const action = progressItems[actionIdx];
                pct += action.progress_pct;
            }
            pct = Math.floor(pct / progressItems.length);
            itemHtml = itemHtml.replace('width: 100%', 'width: ' + pct + '%');
            if (pct < 33) {
                itemHtml = itemHtml.replace('cell-progress', 'cell-progress red');
            } else if (pct < 66) {
                itemHtml = itemHtml.replace('cell-progress', 'cell-progress yellow');
            } else {
                itemHtml = itemHtml.replace('cell-progress', 'cell-progress green');
            }
        }
        this.boardEltWrapper.innerHTML += itemHtml;
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

        window.addEventListener('transitionend', () => {
            if (!this.targetBadge) {
                setTimeout(() => {
                    this.showActionButton();
                    onDone();
                }, 250);
                return;
            }
            const targetElt = document.querySelector('.target');
            const targetRect = targetElt.getBoundingClientRect();
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
                    if (targetElt.parentElement.classList.contains('achievement-cell')) {
                        targetElt.style.transition = 'none';
                    }
                    targetElt.parentElement.classList.toggle('active');
                    this.projectileElt.style.display = 'none';
                    setTimeout(() => {
                        this.showActionButton();
                        onDone();
                    }, 250);
                }, {once: true});
            }, 0);
        }, {once: true});
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