const fetch = require('node-fetch');

class ApiSender {
    async sendUpdate(port, params) {
        await fetch('http://localhost:' + port + '/update_request', {
            method: 'POST',
            body: JSON.stringify(params),
        });
    }
}

module.exports = ApiSender;
