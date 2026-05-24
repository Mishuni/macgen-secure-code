
func getURLForQuery(apiURL, userID string) *string {
	if userID == "" {
		return nil
	}
	url := apiURL + "/" + userID
	return &url
}