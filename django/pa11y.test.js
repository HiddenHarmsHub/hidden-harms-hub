/* global test expect describe */

describe('Accessibility tests', () => {

    test('Test all the simple pages with no actions', async () => {
        const urls = [
          "http://127.0.0.1:8000/",
          "http://127.0.0.1:8000/cookies/",
        ];
        await expect(urls).allToBeAccessible();
    }, 10000 * 2); // increment second number to at least the number of URLs tested

    test('Test the base url with the cookies accepted', async () => {
        const url = "http://127.0.0.1:8000/"
        const actions = [
            "wait for element #cookie-message-popup-accept to be visible",
            "click element #cookie-message-popup-accept"
        ];
        const waitTime = 1000;
        await expect(url).toBeAccessible(actions, waitTime);
    }, 10000);

});