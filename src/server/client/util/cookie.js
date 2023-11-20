
    
    /**
     * Gibt den Wert des Cookies mit dem Schlüssel [key] zurück.
     * Falls der Cookie nicht existiert, wird der Wert [default_value] zurückgegeben.
     * 
     * @param {string} key Cookie-Schlüssel
     * @param {string} defaultValue Default-Wert, falls Cookie unter [key] nicht existiert.
     * @returns {string} Wert des Cookies oder [defaultValue]
     */
    export function getCookieOrDefault(key, defaultValue) {
        var value = Cookies.get(key);
        if (!value) {
            return defaultValue;
        }
        return value;
    }