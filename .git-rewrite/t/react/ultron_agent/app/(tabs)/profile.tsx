import { StyleSheet } from 'react-native';

import { ThemedText } from '@/components/ThemedText';
import { ThemedView } from '@/components/ThemedView';
import { ExternalLink } from '@/components/ExternalLink';
import ParallaxScrollView from '@/components/ParallaxScrollView';
import { IconSymbol } from '@/components/ui/IconSymbol';

export default function ProfileScreen() {
  return (
    <ParallaxScrollView
      headerBackgroundColor={{ light: '#E6E6FA', dark: '#4B0082' }}
      headerImage={
        <IconSymbol
          size={310}
          color="#800080"
          name="person.fill"
          style={styles.headerImage}
        />
      }>
      <ThemedView style={styles.titleContainer}>
        <ThemedText type="title">Profile</ThemedText>
      </ThemedView>

      <ThemedView style={styles.sectionContainer}>
        <ThemedText type="subtitle">User Information</ThemedText>
        <ThemedText style={styles.infoText}>Name: Ultron Agent</ThemedText>
        <ThemedText style={styles.infoText}>Email: ultron.agent@example.com</ThemedText>
        <ThemedText style={styles.infoText}>Member since: 2025</ThemedText>
      </ThemedView>

      <ThemedView style={styles.sectionContainer}>
        <ThemedText type="subtitle">Settings</ThemedText>
        <ThemedText style={styles.settingText}>Notifications: Enabled</ThemedText>
        <ThemedText style={styles.settingText}>Dark Mode: Enabled</ThemedText>
        <ThemedText style={styles.settingText}>Language: English</ThemedText>
      </ThemedView>

      <ThemedView style={styles.sectionContainer}>
        <ThemedText type="subtitle">About</ThemedText>
        <ThemedText>
          This is the Ultron Agent application. It's built with React Native and Expo to provide
          a cross-platform experience for AI-powered assistance.
        </ThemedText>
        <ExternalLink href="https://expo.dev">
          <ThemedText type="link">Learn more about Expo</ThemedText>
        </ExternalLink>
      </ThemedView>
    </ParallaxScrollView>
  );
}

const styles = StyleSheet.create({
  headerImage: {
    color: '#800080',
    bottom: -90,
    left: -35,
    position: 'absolute',
  },
  titleContainer: {
    flexDirection: 'row',
    gap: 8,
  },
  sectionContainer: {
    gap: 8,
    marginBottom: 16,
  },
  infoText: {
    fontSize: 16,
  },
  settingText: {
    fontSize: 16,
  },
});
