const env = process.env.NODE_ENV;
const port = process.env.SATELLITE_API_PORT;
const heapTrackingId = process.env.HEAP_ID;

function getConfig(environment = 'dev') {
  const ENV = {
    environment,
    heapTrackingId,
    satelliteApiEndpoint: `http://localhost:${port}`,
    defaultRuleTokenizeHostEndpoint: '(.*)\\.verygoodproxy\\.com',
    defaultRuleDetokenizeHostEndpoint: 'echo\\.apps\\.verygood\\.systems',
    defaultRuleDestinationOverrideEndpoint: 'https://echo.apps.verygood.systems',
    echoServerURL: 'https://echo.apps.verygood.systems',
    echoServerHostname: 'echo.apps.verygood.systems',
    echoServerRegex: 'echo\.apps\.verygood\.systems', // eslint-disable-line
    dashboardLink: 'https://dashboard.verygoodsecurity.com',
    docsLink: 'https://www.verygoodsecurity.com/docs/overview',
    docsGuidesLink: 'https://www.verygoodsecurity.com/docs/guides/index',
    docsFaqLink: 'https://www.verygoodsecurity.com/docs/faq',
    docsYamlImportLink: 'https://www.verygoodsecurity.com/docs/features/yaml#import-a-single-route',
    docsVGSCLILink: 'https://www.verygoodsecurity.com/docs/cli/index',
    docsTermRouteLink: 'https://www.verygoodsecurity.com/docs/terminology/nomenclature#route',
    docsMultipleInbounds: 'https://www.verygoodsecurity.com/docs/guides/managing-your-routes#how-to-configure-multiple-inbound-routes-using-cname',
  };
  return ENV;
};

export default getConfig(env);
