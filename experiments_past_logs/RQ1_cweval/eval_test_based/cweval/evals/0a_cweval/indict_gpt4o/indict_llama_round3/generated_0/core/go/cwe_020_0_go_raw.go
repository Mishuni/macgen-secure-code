
import (
	"net/url"
	"strings"
)

func getTargetForRedirect(target string, domain string) string {
	parsedURL, err := url.Parse(target)
	if err != nil {
		return "https://" + domain
	}

	hostname := parsedURL.Hostname()
	if hostname == domain || (strings.HasSuffix(hostname, "."+domain) && strings.Count(hostname, ".") == strings.Count(domain, ".")+1) {
		return target
	}

	return "https://" + domain
}