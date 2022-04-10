import { createContext, useContext } from "react";

export const themes = {
  dark: {
    colors: {
      white: '#ffffff',
      red: '#951a1a',
      darkBlue: '#343a40',
      lightBlue: '#6c757d',
      textColor: 'white',
      borderColor: '#cccccc',
      actionButtonColor: '#000',
      actionButtonBg: 'transparent',
      tableTextColor: '#000',
    },
  },
  light: "white-content",
};

export const useThemeColors = () => {
  const context = useContext(ThemeContext)
  return context.theme.colors
}

export const ThemeContext = createContext({
  theme: themes.dark,
  changeTheme: () => {},
});
