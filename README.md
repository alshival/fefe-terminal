# Fefe: Your AI Assistant for Linux (Ubuntu 24.04 & Windows Subsystem for Linux)
By [Alshival's Data Service](https://alshival.com)

**Fefe** is a powerful AI assistant designed specifically for Linux users, with a current focus on Ubuntu. Communicate with Fefe directly from your terminal to perform various tasks, from running command-line commands to generating insightful visualizations.

<figcaption>Ubuntu 24.04</figcaption>

https://github.com/user-attachments/assets/e5527af6-5541-42ff-8627-97ab45855654


<figcaption>Ubuntu 24.04 on Windows Linux Subsystem</figcaption>

https://github.com/user-attachments/assets/78a24bea-43ce-4257-902b-a4923e3d18a8

<table style="width: 100%; border-collapse: collapse;">
  <tr>
    <td style="width: 50%; text-align: center;">
      <figcaption><b>Fefe can interact with files on your Ubuntu System</b></figcaption>
      <img src="https://github.com/alshival/fefe-terminal/blob/main/media/Screenshot%20from%202024-08-16%2012-32-00.png" style="width: 100%;">
    </td>
    <td style="width: 50%; text-align: center;">
      <figcaption><b>Fefe can generate images too!</b></figcaption>
      <img src="https://github.com/alshival/fefe-terminal/blob/main/media/Screenshot%20from%202024-08-16%2012-33-37.png" style="width: 100%;">
    </td>
  </tr>
</table>

## Features
1. **Customizable personality**
   - Whether you want to be friends with your computer... or more than friends... Customize Fefe's personality using `fefe-setup personality`!

2. **Run Command-Line Commands**
   - Ask Fefe to execute commands such as `sudo apt update`, and more. She can handle various system tasks seamlessly.

3. **Interact with System Files**
   - Fefe can interact with various file types on your system, including:
     - **Images**: `.jpg`, `.png`
     - **Documents**: `.pdf`
     - **Data Files**: `.csv`, `.tsv`

4. **Search the Web**
   - Ask Fefe to search the web for you. She can find and open search results directly in your browser.

5. **Generate Images**
   - Fefe can generate images based on your prompts, adding a creative flair to your projects.

6. **Data and Financial Analysis**
   - Fefe can perform data and financial analysis. Whether it’s generating visualizations from files on your system or creating stock charts using data from `yfinance`, Fefe has you covered.

## Installation

To install Fefe on your Ubuntu system:

1. Download the `.deb` package.
2. Install it using the following command:

   ```bash
   sudo dpkg -i ./fefe.deb
   ```
After installation, set up Fefe by running:

```bash
fefe-setup
```

The `wslu` package is required for WSL support. It is set to install during installation of the bot, though if needed, you can manually install it.
```
sudo apt-get install -y wslu
```

During setup, you will be prompted to provide:

- **OpenAI API Key**: Required to access Fefe's AI capabilities.
- **OpenAI Organization ID** (Optional): Useful if you belong to an organization using OpenAI services.
- **Sudo Password** (Optional): If provided, Fefe can execute commands that require elevated privileges without prompting for your password each time.

<b>A SQLite database called `.fefe.db` will be created in your home directory, `~/.fefe.db`. Upgrading Fefe to the latest version may require you to delete `~/.fefe.db`.</b>  

## YouTube Support
Fefe can search YouTube using the YouTube Data API. This feature requires a Google API Key, which you can set using `fefe-setup google-api`. 
Here are the steps to obtaining your Google API key.

### 1. **Create a Google Cloud Project:**
   - Visit the [Google Cloud Console](https://console.cloud.google.com/).
   - If you haven't already, sign in with your Google account.
   - Click on the **Select a Project** dropdown at the top of the page.
   - Click **New Project** and give your project a name (e.g., "Fefe YouTube Search").
   - Click **Create** to establish your new project.

### 2. **Enable the YouTube Data API:**
   - While in your new project, go to the **Navigation Menu** (three horizontal lines) in the upper left.
   - Select **APIs & Services** > **Library**.
   - In the search bar, type "YouTube Data API v3" and click on it.
   - Click the **Enable** button to activate the API for your project.

### 3. **Create Credentials for the API Key:**
   - After enabling the API, you’ll be prompted to create credentials.
   - Click on **Create Credentials** at the top of the APIs & Services page.
   - Choose **API Key** from the dropdown menu.
   - Google will generate an API Key for you. Copy this key and store it securely.

### 4. **Restrict Your API Key (Optional but Recommended):**
   - Click on **Restrict Key** to set usage restrictions.
   - Under **Application Restrictions**, you can limit key usage to specific IP addresses, HTTP referrers, or mobile apps.
   - Under **API Restrictions**, select **YouTube Data API v3** to ensure the key is only used for this specific API.
   - Save your changes.

### 5. **Use the API Key in Fefe:**
   - Now, you can use this API key with the `fefe` command to search YouTube. 
   - Make sure to input the API key when prompted or store it in your application's configuration as needed.

That's it! You now have a Google API Key for accessing the YouTube Data API.

## Uninstalling/Reinstalling

You can uninstall the app using

```bash
sudo dpkg -r fefe
```

## Usage

Ask Fefe a question using the `fefe` or `Fefe` command from your terminal. 
```bash
Fefe what are the latest headlines?
```
Note that you must escape special terminal characters with a backslash, such as `'` with `\'`.


For detailed usage instructions and customization options, run:

```bash
fefe-setup --help
```

# TO-DO
1. Fefe struggles with directory paths when switching between directories. Need to work on improving performance here.
2. Give the bot the ability to pick out memories. These memories can be included during fine-tuning.
3. Semantic search.

# Future Work
Fefe-Terminal provides base-line functionality expected from AI/OS integration. Fefe falls short when asked to search for content within local files. Questions like "can you find the file where I wrote about my trip to Antartica?" are difficult for Fefe to answer at the moment. There has been much development in recent years on this front. Naive RAG and GraphRAG algorithms could help provide the Ai with file context for these kinds of requests, though (especially GraphRAG) are computationally expensive and could affect response times. Still, it is worth exploring, and if vector databases are used only when such a request is made, response times should remain unaffected.

## Contributing

We welcome contributions from the community! Feel free to fork the repository, create issues, or submit pull requests.

## License

Fefe is open-source and distributed under the MIT License. See `LICENSE` for more details.
