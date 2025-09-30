module.exports = function (api) {
  api.cache(true);

  return {
    presets: [
      [
        'babel-preset-expo',
        {
          jsxImportSource: 'react',
          jsxRuntime: 'automatic',
        },
      ],
    ],
    plugins: [
      // Essential plugins only to avoid conflicts
      'react-native-reanimated/plugin',
    ],

    // Fix the babel assumptions based on the warnings
    assumptions: {
      setPublicClassFields: true,
      privateFieldsAsSymbols: true,
    },

    // Environment-specific configurations
    env: {
      production: {
        plugins: [],
      },
    },
  };
};