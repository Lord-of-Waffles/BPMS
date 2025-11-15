const {ZBClient} = require('zeebe-node')
require('dotenv').config

// zeebe setup

const zb = new ZBClient({
    camundaCloud: {
        clientId: process.env.ZEEBE_CLIENT_ID,
        clientSecret: process.env.ZEEBE_CLIENT_SECRET,
        clusterId: process.env.ZEEBE_CLUSTER_ID,
        region: process.env.ZEEBE_REGION || 'bru-2'
    }
})

// create workers

zb.createWorker({
    taskType:'receive_vm_config',
    taskHandler: async (job) => {
        const {json_data, VMRequestID} = job.variables
        console.log("Received VM Request ID: ${VMRequestID} from App Layer with this config: ${json_data}")

        return job.complete({})
    }
})

zb.createWorker({
    taskType:'get-data-centre-availability'
})

zb.createWorker({
    taskType:'start-initialisation',
    taskHandler: async (job) => {
        console.log('-=====================-')
        console.log('Initialising VM...')

    return job.complete({})
    }
})

zb.createWorker({
    taskType:'allocate-ram',
    taskHandler: async (job) => {
        const {json_data} = job.variables
        const vm_size = json_data['VM Size']
        const vm_ram = vm_size === 'smallVM' ? '2GB'
                    : vm_size === 'mediumVM' ? '4GB'
                    : '8GB'

        console.log('Initialising RAM...')
        return job.complete({vm_ram})
    }
})

zb.createWorker({
    taskType:'processing-power',
    taskHandler: async (job) => {
        const {json_data} = job.variables
        const vm_size = json_data['VM Size']
        const vm_vcpu = vm_size === 'smallVM' ? '2 Cores'
                    : vm_size === 'mediumVM' ? '4 Cores'
                    : '8 Cores'
        
        console.log('Initialising vCPU...')
        return job.complete({vm_vcpu})
    }
})

zb.createWorker({
    taskType:'allocate-storage',
    taskHandler: async (job) => {
        const {json_data} = job.variables
        const vm_size = json_data['VM Size']
        const vm_storage = vm_size === 'smallVM' ? '10GB'
                        : vm_size === 'mediumVM' ? '20GB'
                        : '30GB'

        console.log('Initialising VM Storage')
        return job.complete({vm_storage})
    }
})

zb.createWorker({
    taskType:'merge-config',
    taskHandler: async (job) => {
        const {json_data, vm_ram, vm_vcpu, vm_vcpu} = job.variables
        updatedData = {
            ...json_data,
            "VM Ram": vm_ram,
            "VM vCPU": vm_vcpu,
            "VM Storage": vm_storage
        }
        return job.complete({json_data: updatedData})
    }
})
