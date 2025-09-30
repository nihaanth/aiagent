module.exports = {
  // Disable the new architecture for iOS to prevent TurboModule issues
  project: {
    ios: {
      unstable_reactLegacyComponentNames: ['*'],
    },
    android: {},
  },

  // Disable TurboModules and Fabric
  dependencies: {
    'react-native': {
      platforms: {
        android: {
          sourceDir: '../node_modules/react-native/android',
          packageImportPath: 'import io.invertase.firebase.ReactNativeFirebasePackage;',
          buildTypes: [],
        },
        ios: {
          project: '../node_modules/react-native/React.xcodeproj',
          sharedLibraries: [],
          libraryFolder: 'Libraries',
        },
      },
    },
  },

  // Force legacy architecture
  platforms: {
    ios: {
      linkConfig: () => ({}),
      projectConfig: () => ({}),
      dependencyConfig: () => ({}),
    },
  },
};