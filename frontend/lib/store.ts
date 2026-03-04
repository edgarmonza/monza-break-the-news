import { create } from 'zustand';
import { persist } from 'zustand/middleware';

export interface SavedStory {
  id: string;
  title: string;
  summary: string;
  image_url?: string;
  source?: string;
  saved_at: string;
}

interface PluralStore {
  // Onboarding
  onboardingComplete: boolean;
  completeOnboarding: () => void;
  resetOnboarding: () => void;

  // Followed topics & outlets
  followedTopics: string[];
  followedOutlets: string[];
  toggleFollowTopic: (topicId: string) => void;
  toggleFollowOutlet: (outletId: string) => void;
  setFollowedTopics: (topics: string[]) => void;
  setFollowedOutlets: (outlets: string[]) => void;

  // Saved stories
  savedStories: SavedStory[];
  saveStory: (story: SavedStory) => void;
  unsaveStory: (storyId: string) => void;
  isStorySaved: (storyId: string) => boolean;

  // Preferences
  region: string;
  setRegion: (region: string) => void;
  showSummariesByDefault: boolean;
  setShowSummariesByDefault: (show: boolean) => void;

  // Active filters (persisted so they survive refresh)
  activeTopic: string;
  activeCountry: string;
  setActiveTopic: (topic: string) => void;
  setActiveCountry: (country: string) => void;
}

export const useStore = create<PluralStore>()(
  persist(
    (set, get) => ({
      // Onboarding
      onboardingComplete: false,
      completeOnboarding: () => set({ onboardingComplete: true }),
      resetOnboarding: () => set({ onboardingComplete: false }),

      // Followed topics & outlets
      followedTopics: [],
      followedOutlets: [],
      toggleFollowTopic: (topicId) =>
        set((state) => ({
          followedTopics: state.followedTopics.includes(topicId)
            ? state.followedTopics.filter((t) => t !== topicId)
            : [...state.followedTopics, topicId],
        })),
      toggleFollowOutlet: (outletId) =>
        set((state) => ({
          followedOutlets: state.followedOutlets.includes(outletId)
            ? state.followedOutlets.filter((o) => o !== outletId)
            : [...state.followedOutlets, outletId],
        })),
      setFollowedTopics: (topics) => set({ followedTopics: topics }),
      setFollowedOutlets: (outlets) => set({ followedOutlets: outlets }),

      // Saved stories
      savedStories: [],
      saveStory: (story) =>
        set((state) => {
          if (state.savedStories.some((s) => s.id === story.id)) return state;
          return { savedStories: [story, ...state.savedStories] };
        }),
      unsaveStory: (storyId) =>
        set((state) => ({
          savedStories: state.savedStories.filter((s) => s.id !== storyId),
        })),
      isStorySaved: (storyId) => get().savedStories.some((s) => s.id === storyId),

      // Preferences
      region: 'all',
      setRegion: (region) => set({ region }),
      showSummariesByDefault: false,
      setShowSummariesByDefault: (show) => set({ showSummariesByDefault: show }),

      // Active filters
      activeTopic: 'all',
      activeCountry: 'all',
      setActiveTopic: (topic) => set({ activeTopic: topic }),
      setActiveCountry: (country) => set({ activeCountry: country }),
    }),
    {
      name: 'plural-storage',
      partialize: (state) => ({
        onboardingComplete: state.onboardingComplete,
        followedTopics: state.followedTopics,
        followedOutlets: state.followedOutlets,
        savedStories: state.savedStories,
        region: state.region,
        showSummariesByDefault: state.showSummariesByDefault,
        activeTopic: state.activeTopic,
        activeCountry: state.activeCountry,
      }),
    }
  )
);
