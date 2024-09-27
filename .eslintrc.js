module.exports = {
    extends: "eslint:recommended",
    env: {
        browser: true,
        node: true,
    },
    parserOptions: { ecmaVersion: 9 },
    globals: {
        $: "readonly",
    },
};
