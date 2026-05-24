
import (
	"net/url"
	"strings"
)

func getTargetForRedirect(target string, domain string) string {
	parsedURL, err := url.Parse(target)
	if err != nil {
		return "https://" + domain
	}

	if strings.HasSuffix(parsedURL.Hostname(), domain) {
		return target
	}

	return "https://" + domain
}