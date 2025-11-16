const express = require('express');
const server = express();
server.use(express.json());

// Data Centre Enum
const DataCentre = Object.freeze({
    LONDON: { id: 1, name: 'London', region: 'EU-West' },
    FRANKFURT: { id: 2, name: 'Frankfurt', region: 'EU-Central' },
    AMSTERDAM: { id: 3, name: 'Amsterdam', region: 'EU-North' }
});

const DATA_CENTRES = Object.values(DataCentre);

function random() {
    let randomNo = Math.floor(Math.random() * 100);
    console.log(randomNo);
    return randomNo;
}

function dataCentreAvailability() {
    return DATA_CENTRES.map(centre => ({
        ...centre,
        availability: random()
    }));
}

server.get("/availability", (request, response) => {
    const dataCentres = dataCentreAvailability();
    
    const bestCentre = dataCentres.reduce((best, current) => 
        current.availability > best.availability ? current : best
    );
    
    response.json({
        bestCentre: {
            id: bestCentre.id,
            name: bestCentre.name,
            region: bestCentre.region,
            availability: bestCentre.availability
        },
        allCentres: dataCentres
    });
});

const port = 3000;

server.listen(port, () => {
    console.log(`Server listening on port: ${port}`);
});

module.exports = server;