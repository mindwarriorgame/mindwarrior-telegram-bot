class ServerTime {
    constructor() {
        this.clientStartedAt = parseInt(window.localStorage.getItem('clientTime') || Date.now());
        this.serverStartedAt = parseInt(window.localStorage.getItem('serverTime') || Date.now());
        let syncOffset = () => {};
        syncOffset = () => {
            const started = Date.now();
            let finished = Date.now();
            fetch('https://boo.great-site.net/time.php', {method: 'POST', mode: 'cors'})
                .then(response => {
                    if (response.ok) {
                        finished = Date.now();
                        return response.text();
                    } else {
                        throw new Error('Network response was not ok');
                    }
                })
                .then(serverTime => {
                    this.serverStartedAt = parseInt(serverTime) * 1000;
                    this.clientStartedAt = Date.now() - Math.floor((finished - started) / 2);

                    window.localStorage.setItem('serverTime', this.serverStartedAt);
                    window.localStorage.setItem('clientTime', this.clientStartedAt);

                    console.log("Server time offset: " + (this.serverStartedAt - this.clientStartedAt) + "ms");
                }).catch(err => {
                console.error(err);
                setTimeout(syncOffset, 1000);
            });
        };
        syncOffset();
    }

    now() {
        return this.serverStartedAt + (Date.now() - this.clientStartedAt);
    }
}