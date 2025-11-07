function random() {
  let randomNo = Math.floor(Math.random() * 100);
  console.log(randomNo);
  return randomNo; //
}

function dataCentreAvailability(){
    const centre1 = random();
    const centre2 = random();
    const centre3 = random();
    return [centre1, centre2, centre3];
}

const express = require('express');

const server = express();
server.use(express.json());

const port = 3000;

server.listen(port, () => {
    console.log(`Server listening on port: ${port}`);
});

server.get("/availability", (request, response) => {
    const dataCentres = dataCentreAvailability();
    const bestCentreAvailability = Math.max(...dataCentres);
    const bestCentreIndex = dataCentres.indexOf(bestCentreAvailability);
    
    response.json({
        bestCentre: bestCentreIndex + 1,
        availability: bestCentreAvailability,
        allCentres: dataCentres
    });
});