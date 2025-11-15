const { ZBClient } = require('zeebe-node');
require('dotenv').config();

const zb = new ZBClient({
  camundaCloud: {
    clientId: process.env.ZEEBE_CLIENT_ID,
    clientSecret: process.env.ZEEBE_CLIENT_SECRET,
    clusterId: process.env.ZEEBE_CLUSTER_ID,
    region: process.env.ZEEBE_REGION || 'bru-2'
  }
});

zb.createWorker({
    taskType: "start-initialisation",
    taskHandler: async (job) => {
        console.log("-=====================-");
        console.log("Initialising VM...");
        return job.complete({});
    }
});

zb.createWorker({
    taskType: "allocate-ram",
    taskHandler: async (job) => {
        const { json_data } = job.variables;
        const vmSize = json_data["VM Size"];
        
        const vm_ram = vmSize === "smallVM" ? "2GB" 
                     : vmSize === "mediumVM" ? "4GB" 
                     : "8GB";
        
        console.log('Initialising RAM...')
        return job.complete({ vm_ram });
    }
});

zb.createWorker({
    taskType: "processing-power",
    taskHandler: async (job) => {
        const { json_data } = job.variables;
        const vmSize = json_data["VM Size"];
        
        const vm_vcpu = vmSize === "smallVM" ? "2 Cores" 
                      : vmSize === "mediumVM" ? "4 Cores" 
                      : "8 Cores";
        
        console.log('Initialising vCPU...')
        return job.complete({ vm_vcpu });
    }
});

zb.createWorker({
    taskType: "allocate-storage",
    taskHandler: async (job) => {
        const { json_data } = job.variables;
        const vmSize = json_data["VM Size"];
        
        const vm_storage = vmSize === "smallVM" ? "10 GB" 
                         : vmSize === "mediumVM" ? "20 GB" 
                         : "30 GB";
        
        console.log('Initialising VM Storage...')
        return job.complete({ vm_storage });
    }
});

zb.createWorker({
    taskType: "merge-config",
    taskHandler: async (job) => {
        const { json_data, vm_ram, vm_vcpu, vm_storage } = job.variables;
        
        console.log("Merging configuration from parallel tasks...");
        
        const updated_data = {
            ...json_data,
            "VM Ram": vm_ram,
            "VM vCPU": vm_vcpu,
            "VM Storage": vm_storage
        };
        
        console.log("Configuration merged successfully");
        
        return job.complete({ json_data: updated_data });
    }
});

zb.createWorker({
    taskType: "send-result",
    taskHandler: async (job) => {
        console.log("VM Initialisation complete, sending result...");
        return job.complete({});
    }
});

zb.createWorker({
    taskType: "get-data-centre-availability",
    taskHandler: async (job) => {
        console.log("Checking data centre availability...");
        
        const dataCentres = [
            Math.floor(Math.random() * 100),
            Math.floor(Math.random() * 100),
            Math.floor(Math.random() * 100)
        ];
        
        const bestCentreAvailability = Math.max(...dataCentres);
        const bestCentreIndex = dataCentres.indexOf(bestCentreAvailability);
        
        const availability = {
            bestCentre: bestCentreIndex + 1,
            availability: bestCentreAvailability,
            allCentres: dataCentres
        };
        
        console.log(`Best centre: ${availability.bestCentre} (${availability.availability}% available)`);
        
        return job.complete({ DataCentreAvailability: availability });
    }
});

console.log("All Zeebe workers registered and ready!");

module.exports = zb;