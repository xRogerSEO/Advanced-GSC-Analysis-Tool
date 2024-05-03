import streamlit as st
from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build
import pandas as pd

# Assuming the analysis functions such as perform_combined_analysis and classify_urls
# are defined in separate modules that have been imported properly.

# Setup Google API OAuth
def load_config():
    """Load client configuration for Google API OAuth."""
    return {
        "installed": {
            "client_id": str(st.secrets["installed"]["client_id"]),
            "client_secret": str(st.secrets["installed"]["client_secret"]),
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": "https://accounts.google.com/o/oauth2/token",
            "redirect_uris": [st.secrets["installed"]["redirect_uris"][0]],
        }
    }

def init_oauth_flow():
    """Initialize OAuth flow using client configuration."""
    client_config = load_config()
    scopes = ["https://www.googleapis.com/auth/webmasters"]
    return Flow.from_client_config(client_config, scopes=scopes, redirect_uri=client_config["installed"]["redirect_uris"][0])

def authenticate_user():
    """Generate authentication URL for user to authenticate with Google API."""
    flow = init_oauth_flow()
    auth_url, _ = flow.authorization_url(prompt='consent')
    return flow, auth_url

def fetch_gsc_data(service, site_url, start_date, end_date):
    """Fetch data from Google Search Console API."""
    request = {
        'startDate': start_date,
        'endDate': end_date,
        'dimensions': ['query', 'page', 'country', 'device'],
        'rowLimit': 10000
    }
    response = service.searchanalytics().query(siteUrl=site_url, body=request).execute()
    return pd.DataFrame(response.get('rows', []))

def main():
    st.title('Advanced GSC Analysis Tool')
    st.image("https://assets-global.website-files.com/630ce5588e0922095e53ed04/6315bf5e44c1d266a72eb226_61b501ad93792309a253a3b3_p.%20(1)%20(1).svg", width=200)

    st.markdown("""<p>Created by <a href="https://pneumallc.com/" target="_blank">Pneuma LLC</a></p>""", unsafe_allow_html=True)
    st.divider()

    if 'auth_flow' not in st.session_state:
        st.session_state['auth_flow'], auth_url = authenticate_user()
        st.markdown(f'Please authenticate using [this link]({auth_url}).', unsafe_allow_html=True)

    if 'auth_flow' in st.session_state:
        code = st.text_input("Enter the authentication code here:")
        if st.button('Authenticate'):
            st.session_state['credentials'] = st.session_state['auth_flow'].fetch_token(code=code)
            st.success("Authentication successful! You can now fetch data.")

    if 'credentials' in st.session_state:
        site_url = st.text_input("Enter the GSC site URL")
        start_date = st.date_input("Start Date")
        end_date = st.date_input("End Date")
        if st.button("Fetch Data"):
            service = build('webmasters', 'v3', credentials=st.session_state['credentials'])
            data = fetch_gsc_data(service, site_url, start_date.isoformat(), end_date.isoformat())
            st.subheader("Fetched Data")
            st.dataframe(data)
            # Assuming perform_combined_analysis and classify_urls are ready to use
            # analysis_results, detailed_lists = perform_combined_analysis(data)
            # st.subheader("Analysis Results")
            # st.json(analysis_results)
            # classified_data = classify_urls(data)
            # st.subheader("URL Classification")
            # st.dataframe(classified_data)

if __name__ == "__main__":
    main()
