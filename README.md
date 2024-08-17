# Fefe: Your AI Assistant for Linux (Ubuntu & Windows Linux Subsystem)
By [Alshival's Data Service](https://alshival.com)

**Fefe** is a powerful AI assistant designed specifically for Linux users, with a current focus on Ubuntu. Communicate with Fefe directly from your terminal to perform various tasks, from running command-line commands to generating insightful visualizations.

<figcaption><b>Fefe can write/execute command line and python code</b></figcaption>
<img src="https://github.com/alshival/fefe-terminal/blob/main/media/Screenshot%20from%202024-08-17%2002-25-56.png">

<figcaption><b>Fefe can interact with files on your Ubuntu System</b></figcaption>
<img src="https://github.com/alshival/fefe-terminal/blob/main/media/Screenshot%20from%202024-08-16%2012-32-00.png">

<figcaption><b>Fefe can generate images too!</b></figcaption>
<img src="https://github.com/alshival/fefe-terminal/blob/main/media/Screenshot%20from%202024-08-16%2012-33-37.png">

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

## Setup

After installation, set up Fefe by running:

```bash
fefe-setup
```

During setup, you will be prompted to provide:

- **OpenAI API Key**: Required to access Fefe's AI capabilities.
- **OpenAI Organization ID** (Optional): Useful if you belong to an organization using OpenAI services.
- **Sudo Password** (Optional): If provided, Fefe can execute commands that require elevated privileges without prompting for your password each time.

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
1. Add token limit check using tiktoken.
2. Clean up the `fefe-setup` scripts to use SQL `UPDATE` commands instead of the `set_config`. This will clean up the code significantly and make it easier to maintain.
3. Give the bot the ability to pick out memories. These memories can be included during fine-tuning.

## Contributing

We welcome contributions from the community! Feel free to fork the repository, create issues, or submit pull requests.

## License

Fefe is open-source and distributed under the MIT License. See `LICENSE` for more details.
