export const topNavStore = defineStore("topNavStore", {
  state: () => ({
    isNavAppear: useLocalStorage("topNavStore", true),
  }),
  actions: {
    set(isNavAppear: boolean) {
      this.isNavAppear = isNavAppear;
    },
    toggle() {
      this.isNavAppear = !this.isNavAppear;
    },
  },
});

export const serverStore = defineStore("serverStore", {
  state: () => ({
    isServerRunning: false,
  }),
  actions: {
    set(isServerRunning: boolean) {
      this.isServerRunning = isServerRunning;
    },
    toggle() {
      this.isServerRunning = !this.isServerRunning;
    },
  },
});
