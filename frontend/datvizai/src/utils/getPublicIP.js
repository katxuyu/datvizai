export async function getPublicIP() {
    try {
      const response = await fetch("https://api64.ipify.org?format=json");
      const data = await response.json();
      return data.ip; // Returns the user's public IP
    } catch (error) {
      console.error("Failed to fetch public IP:", error);
      return null;
    }
  }
  