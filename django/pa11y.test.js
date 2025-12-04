/* global test expect describe */

const colourSchemes = ['light', 'dark']

describe('Accessibility tests', () => {

    test('Test all the simple pages with no actions', async () => {
        const urls = [
          "http://127.0.0.1:8000/",
          "http://127.0.0.1:8000/cookies/",
          "http://127.0.0.1:8000/multiplesystemsestimation",
          "http://127.0.0.1:8000/multiplesystemsestimation/calculator",
        ];
        for (let i = 0; i < colourSchemes.length; i += 1) {
            await expect(urls).allToBeAccessible(colourSchemes[i]);
        }
        
    }, 10000 * 8); // increment second number to at least the number of URLs tested * number of colour schemes

    test('Test the base url with the cookies accepted', async () => {
        const url = "http://127.0.0.1:8000/"
        const actions = [
            "wait for element #cookie-message-popup-accept to be visible",
            "click element #cookie-message-popup-accept",
        ];
        const waitTime = 1000;
        for (let i = 0; i < colourSchemes.length; i += 1) {
            await expect(url).toBeAccessible(actions, waitTime, colourSchemes[i], true);
        }
    }, 10000);

    test('Test the generated mse form', async () => {
        const url = "http://127.0.0.1:8000/multiplesystemsestimation/calculator"
        const actions = [
            "wait for element #id_total_lists_required to be visible",
            "wait for element #submit-button to be visible",
            "set field #id_total_lists_required to 6",
            "click element #submit-button",
            "wait for element .input-table to be visible",
        ];
        const waitTime = 1000;
        for (const scheme of colourSchemes) {
          await expect(url).toBeAccessible(actions, waitTime, scheme);
        }
    }, 10000);

});