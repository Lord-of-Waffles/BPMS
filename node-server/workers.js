const { ZBClient } = require('zeebe-node');
const {MongoClient} = require('mongodb')
const fs = require('fs')
const path = require('path')
require('dotenv').config();

const zb = new ZBClient({
  camundaCloud: {
    clientId: process.env.ZEEBE_CLIENT_ID,
    clientSecret: process.env.ZEEBE_CLIENT_SECRET,
    clusterId: process.env.ZEEBE_ADDRESS.split('.')[0], // Extract cluster ID from address
    region: process.env.CAMUNDA_CLOUD_REGION || 'bru-2'
  }
});

// mongodb setup
let mongoClient = null;
let db = null;

async function connectMongo() {
    try {
        mongoClient = new MongoClient(process.env.MONGO_URI, {
            tlsAllowInvalidCertificates: true
        });
        await mongoClient.connect();
        db = mongoClient.db(process.env.MONGO_DB);
        console.log('Connected to MongoDB');
    } catch (error) {
        console.error('MongoDB connection failed:', error);
    }
}

// Connect to MongoDB
connectMongo();

zb.createWorker({
    taskType: "start-initialisation",
    taskHandler: async (job) => {
        const { json_data } = job.variables;
        const dateNeeded = json_data["Date Needed"];
        
        // CONSTRAINT: Check if date is in the future
        const requestedDate = new Date(dateNeeded);
        const today = new Date();
        const daysUntilNeeded = Math.ceil((requestedDate - today) / (1000 * 60 * 60 * 24));
        
        if (daysUntilNeeded < 2) {
            return job.error(
                'INSUFFICIENT_LEAD_TIME',
                `VM needed in ${daysUntilNeeded} days. Minimum lead time is 2 days for provisioning.`
            );
        }
        
        console.log(`Date constraint satisfied: ${daysUntilNeeded} days lead time`);
        console.log("-=====================-");
        console.log("Initialising VM...");
        
        return job.complete({ daysUntilNeeded });
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


console.log("All Zeebe workers registered and ready!");

// Worker 7: Save Config to MongoDB (NEW - moved from Python)
zb.createWorker({
    taskType: "save-config-mongodb",
    taskHandler: async (job) => {
        const { json_data } = job.variables;
        
        console.log("Saving configuration to MongoDB...");
        
        try {
            if (!db) {
                throw new Error('MongoDB not connected');
            }
            
            // Ping MongoDB
            await db.admin().ping();
            console.log("✓ MongoDB connection verified");
            
            // Insert document
            const vmsCollection = db.collection('vms');
            const result = await vmsCollection.insertOne(json_data);
            
            console.log(`Saved to MongoDB with ID: ${result.insertedId}`);
            
            return job.complete({
                dbVMId: result.insertedId.toString(),
                dbSaveSuccess: true,
                dbSaveTimestamp: new Date().toISOString()
            });
            
        } catch (error) {
            console.error('MongoDB save failed:', error);
            return job.fail(`Failed to save to MongoDB: ${error.message}`);
        }
    }
});

zb.createWorker({
    taskType: "save-config-csv",
    taskHandler: async (job) => {
        const { json_data } = job.variables;
        
        console.log("Saving configuration to CSV...");
        
        try {
            const csvPath = path.join(__dirname, 'saved_config.csv');
            
            // Convert object to CSV format (simple implementation)
            // Format: key|value pairs separated by spaces
            const csvRow = Object.entries(json_data)
                .map(([key, value]) => {
                    // Handle arrays and objects
                    if (Array.isArray(value)) {
                        return `${key}|${value.join(',')}`;
                    } else if (typeof value === 'object') {
                        return `${key}|${JSON.stringify(value)}`;
                    }
                    return `${key}|${value}`;
                })
                .join(' ');
            
            // Write to CSV file (overwrites existing file)
            fs.writeFileSync(csvPath, csvRow + '\n', 'utf8');
            
            console.log(`Saved to CSV at: ${csvPath}`);
            
            return job.complete({
                csvSaveSuccess: true,
                csvPath: csvPath
            });
            
        } catch (error) {
            console.error('CSV save failed:', error);
            return job.fail(`Failed to save to CSV: ${error.message}`);
        }
    }
});
    

module.exports = zb;