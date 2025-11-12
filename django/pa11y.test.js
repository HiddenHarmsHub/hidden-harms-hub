/* global test expect describe */

describe('Accessibility tests', () => {

    test('Test all the simple pages with no actions', async () => {
        const urls = [
          "http://127.0.0.1:8000/",
          "http://127.0.0.1:8000/cookies/",
          "http://127.0.0.1:8000/multiplesystemsestimation",
          "http://127.0.0.1:8000/multiplesystemsestimation/calculator",
        ];
        await expect(urls).allToBeAccessible();
    }, 10000 * 2); // increment second number to at least the number of URLs tested

    test('Test the base url with the cookies accepted', async () => {
        const url = "http://127.0.0.1:8000/"
        const actions = [
            "wait for element #cookie-message-popup-accept to be visible",
            "click element #cookie-message-popup-accept",
        ];
        const waitTime = 1000;
        await expect(url).toBeAccessible(actions, waitTime);
    }, 10000);

    test('Test the generated mse form', async () => {
        const url = "http://127.0.0.1:8000/multiplesystemsestimation/calculator"
        const actions = [
            "wait for element #id_total_lists_required to be visible",
            "wait for element #submit-button to be visible",
            "set field #id_total_lists_required to 6",
            "click element #submit-button",
            "wait for element #input-table to be visible",
        ];
        const waitTime = 1000;
        await expect(url).toBeAccessible(actions, waitTime);
    }, 10000);

});