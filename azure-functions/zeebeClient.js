const { ZBClient } = require("zeebe-node");

const zb = new ZBClient({
  camundaCloud: {
    clientId: process.env.ZEEBE_CLIENT_ID,
    clientSecret: process.env.ZEEBE_CLIENT_SECRET,
    clusterId: process.env.ZEEBE_CLUSTER_ID,
    region: process.env.ZEEBE_REGION
  }
});

module.exports = zb;
