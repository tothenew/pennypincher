## Slack App Creation and OAuth Token Generation

### Aim 

The aim create a Slack app along with OAuth token to permit Penny Pincher to upload files on slack channel.

### Setup

1. Go to [Slack API Page](https://api.slack.com/apps) and click on **Create an app**.

![Alt](/images/slack_app_setup/create_slack_app_1.png)

2. Give your application a name and select the workspace.

![Alt](/images/slack_app_setup/give_app_name_2.png)

3. A Basic Information page will open, Click on **Oauth and Permissions** option present at the left side of the page under Features.

![Alt](/images/slack_app_setup/basic_info_page_3.png)

4. In the OAuth and Permissions page, scroll down to Scopes. Two types of scopes are seen. Bot Token Scopes and User Token Scopes. We need to set scopes under Bot Token Scopes hence, Click on **Add an OAuth Scope** under Bot Token Scopes.

![Alt](/images/slack_app_setup/scopes_selection_4.png)

5. Select Chats:Write, File:Write permissions.

![Alt](/images/slack_app_setup/select_permissions_1_5.png)

![Alt](/images/slack_app_setup/select_permissions_2_5.png)

6. Now scroll above and click on **Install To Workspace** button under OAuth Tokens & Redirect URL.

![Alt](/images/slack_app_setup/install_to_workspace_6.png)

7. The following page appears. Click on **Allow**.

![Alt](/images/slack_app_setup/click_on_allow_7.png)

8. A bot token will be generated. This is the slack token to be filled in Cloudformation Template.

![Alt](/images/slack_app_setup/oauth_token_8.png)