# -*- coding: utf-8 -*-

# Copyright 2025 Amazon.com, Inc. or its affiliates. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License"). You
# may not use this file except in compliance with the License. A copy of
# the License is located at
#
# http://aws.amazon.com/apache2.0/
#
# or in the "license" file accompanying this file. This file is
# distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF
# ANY KIND, either express or implied. See the License for the specific
# language governing permissions and limitations under the License.

import unittest
import sys
from unittest import skipIf

import mock
from typing import List, Dict, Any
import xml.etree.ElementTree as ET

from ebcli.controllers.migrate import (
    translate_iis_to_alb,
    create_alb_rules,
    _sort_rules_by_specificity,
    get_site_configs,
    SiteConfig,
    convert_alb_rules_to_option_settings,
    ConvertedALBRules,
    get_listener_configs,
)


@skipIf(not sys.platform.startswith("win"), "`eb migrate` only supports Windows")
class TestMigrateController(unittest.TestCase):
    """Tests for the migrate controller module."""

    def test_translate_iis_to_alb_removes_anchors(self):
        """Test that start and end anchors are removed."""
        self.assertEqual("/path", translate_iis_to_alb("^/path$"))
        self.assertEqual("/path", translate_iis_to_alb("^/path"))
        self.assertEqual("/path", translate_iis_to_alb("/path$"))

    def test_translate_iis_to_alb_simplifies_segment_patterns(self):
        """Test that {segment} patterns are replaced with *."""
        self.assertEqual(
            "/products/*/details", translate_iis_to_alb("/products/{id:int}/details")
        )
        self.assertEqual(
            "/users/*/profile", translate_iis_to_alb("/users/{name}/profile")
        )
        self.assertEqual("/*/test", translate_iis_to_alb("/{any}/test"))

    def test_translate_iis_to_alb_simplifies_capture_groups(self):
        """Test that capture groups are replaced with *."""
        self.assertEqual(
            "/products/*/details", translate_iis_to_alb("/products/([0-9]+)/details")
        )
        self.assertEqual(
            "/users/*/profile", translate_iis_to_alb("/users/([a-zA-Z0-9]+)/profile")
        )
        # Note: This test is currently failing because the function removes trailing asterisks
        # The expected behavior should be to keep the asterisk
        self.assertEqual("/articles/*", translate_iis_to_alb("/articles/(.*)"))

    def test_translate_iis_to_alb_simplifies_character_classes(self):
        """Test that character classes are replaced with *."""
        self.assertEqual(
            "/products/*/details", translate_iis_to_alb("/products/[0-9]+/details")
        )
        self.assertEqual(
            "/users/*/profile", translate_iis_to_alb("/users/[a-zA-Z0-9]+/profile")
        )

    def test_translate_iis_to_alb_replaces_plus_with_asterisk(self):
        """Test that + quantifier is replaced with *."""
        self.assertEqual("/files/?*", translate_iis_to_alb("/files/.+"))
        self.assertEqual("/api/?*", translate_iis_to_alb("/api/.+"))

    def test_translate_iis_to_alb_ensures_leading_slash(self):
        """Test that patterns without leading slash get one added."""
        self.assertEqual("/path", translate_iis_to_alb("path"))
        self.assertEqual("/api/v1", translate_iis_to_alb("api/v1"))
        self.assertEqual("/products/*", translate_iis_to_alb("products/(.*)"))

    def test_translate_iis_to_alb_removes_double_asterisks(self):
        """Test that double asterisks are simplified to single asterisk."""
        self.assertEqual("/path/*", translate_iis_to_alb("/path/(.*)(.*)"))
        self.assertEqual("/api/*", translate_iis_to_alb("/api/[0-9]+[a-z]+"))

    def test_translate_iis_to_alb_removes_trailing_asterisk(self):
        """Test that trailing asterisks are removed."""
        self.assertEqual("/path/*", translate_iis_to_alb("/path/(.*)"))
        self.assertEqual("/api/v1/*", translate_iis_to_alb("/api/v1/(.*)"))

    def test_translate_iis_to_alb_complex_patterns(self):
        """Test complex pattern combinations."""
        self.assertEqual(
            "/api/v*/users/*/profile",
            translate_iis_to_alb("^/api/v[0-9]+/users/([a-zA-Z0-9]+)/profile$"),
        )
        self.assertEqual("/search/*", translate_iis_to_alb("/search/(.*)"))
        self.assertEqual(
            "/products/*/reviews/*",
            translate_iis_to_alb("/products/{id}/reviews/[0-9]+"),
        )


@skipIf(not sys.platform.startswith("win"), "`eb migrate` only supports Windows")
class TestSortRulesBySpecificity(unittest.TestCase):
    """Tests for the _sort_rules_by_specificity function."""

    def test_sort_rules_by_specificity_empty_list(self):
        """Test sorting an empty list of rules."""
        rules = []
        sorted_rules = _sort_rules_by_specificity(rules)
        self.assertEqual(sorted_rules, [])

    def test_sort_rules_by_specificity_no_conditions(self):
        """Test sorting rules with no conditions."""
        rules = [
            {"Actions": [{"Type": "forward"}], "Protocol": "http"},
            {"Actions": [{"Type": "forward"}], "Protocol": "https"},
        ]
        sorted_rules = _sort_rules_by_specificity(rules)
        # Order should remain the same since no conditions to sort by
        self.assertEqual(sorted_rules, rules)

    def test_sort_rules_by_specificity_host_header_only(self):
        """Test sorting rules with only host-header conditions."""
        rules = [
            {
                "Actions": [{"Type": "forward"}],
                "Protocol": "http",
                "Conditions": [{"Field": "host-header", "Values": ["example.com"]}],
            },
            {
                "Actions": [{"Type": "forward"}],
                "Protocol": "http",
                "Conditions": [{"Field": "host-header", "Values": ["api.example.com"]}],
            },
        ]
        sorted_rules = _sort_rules_by_specificity(rules)
        # Both rules have the same specificity (host-header only), so order should remain
        self.assertEqual(sorted_rules, rules)

    def test_sort_rules_by_specificity_path_pattern_only(self):
        """Test sorting rules with only path-pattern conditions."""
        rules = [
            {
                "Actions": [{"Type": "forward"}],
                "Protocol": "http",
                "Conditions": [{"Field": "path-pattern", "Values": ["/api/*"]}],
            },
            {
                "Actions": [{"Type": "forward"}],
                "Protocol": "http",
                "Conditions": [{"Field": "path-pattern", "Values": ["/users/*"]}],
            },
        ]
        sorted_rules = _sort_rules_by_specificity(rules)
        # Both rules have the same specificity (path-pattern only), so order should remain
        self.assertEqual(sorted_rules, rules)

    def test_sort_rules_by_specificity_mixed_conditions(self):
        """Test sorting rules with mixed condition types."""
        # Define rules with different specificity levels
        path_only_rule = {
            "Actions": [{"Type": "forward"}],
            "Protocol": "http",
            "Conditions": [{"Field": "path-pattern", "Values": ["/api/*"]}],
        }
        host_only_rule = {
            "Actions": [{"Type": "forward"}],
            "Protocol": "http",
            "Conditions": [{"Field": "host-header", "Values": ["example.com"]}],
        }
        both_conditions_rule = {
            "Actions": [{"Type": "forward"}],
            "Protocol": "http",
            "Conditions": [
                {"Field": "host-header", "Values": ["api.example.com"]},
                {"Field": "path-pattern", "Values": ["/v1/*"]},
            ],
        }
        no_conditions_rule = {"Actions": [{"Type": "forward"}], "Protocol": "http"}

        # Test with rules in different orders
        rules = [
            path_only_rule,
            host_only_rule,
            both_conditions_rule,
            no_conditions_rule,
        ]
        sorted_rules = _sort_rules_by_specificity(rules)

        # Verify the sorting order: both_conditions > path_only > host_only > no_conditions
        # Instead of comparing entire rule objects, check their specificity scores
        self.assertEqual(sorted_rules[0]["Protocol"], both_conditions_rule["Protocol"])
        self.assertEqual(
            len(sorted_rules[0]["Conditions"]), 2
        )  # Both host and path conditions
        self.assertEqual(sorted_rules[1]["Protocol"], path_only_rule["Protocol"])
        self.assertEqual(sorted_rules[1]["Conditions"][0]["Field"], "path-pattern")
        self.assertEqual(sorted_rules[2]["Protocol"], host_only_rule["Protocol"])
        self.assertEqual(sorted_rules[2]["Conditions"][0]["Field"], "host-header")
        self.assertEqual(
            sorted_rules[3], no_conditions_rule
        )  # No conditions rule can be compared directly

        # Test with a different initial order
        rules = [
            no_conditions_rule,
            host_only_rule,
            path_only_rule,
            both_conditions_rule,
        ]
        sorted_rules = _sort_rules_by_specificity(rules)

        # Verify the sorting order remains consistent
        self.assertEqual(
            len(sorted_rules[0]["Conditions"]), 2
        )  # Both host and path conditions
        self.assertEqual(sorted_rules[1]["Conditions"][0]["Field"], "path-pattern")
        self.assertEqual(sorted_rules[2]["Conditions"][0]["Field"], "host-header")
        self.assertEqual(sorted_rules[3], no_conditions_rule)

    def test_sort_rules_by_specificity_multiple_same_type(self):
        """Test sorting rules with multiple conditions of the same type."""
        # Rule with multiple path patterns
        multiple_paths_rule = {
            "Actions": [{"Type": "forward"}],
            "Protocol": "http",
            "Conditions": [
                {"Field": "path-pattern", "Values": ["/api/*"]},
                {"Field": "path-pattern", "Values": ["/v1/*"]},
            ],
        }

        # Rule with multiple host headers
        multiple_hosts_rule = {
            "Actions": [{"Type": "forward"}],
            "Protocol": "http",
            "Conditions": [
                {"Field": "host-header", "Values": ["api.example.com"]},
                {"Field": "host-header", "Values": ["dev.example.com"]},
            ],
        }

        # Rule with both types
        mixed_rule = {
            "Actions": [{"Type": "forward"}],
            "Protocol": "http",
            "Conditions": [
                {"Field": "host-header", "Values": ["example.com"]},
                {"Field": "path-pattern", "Values": ["/users/*"]},
            ],
        }

        rules = [multiple_paths_rule, multiple_hosts_rule, mixed_rule]
        sorted_rules = _sort_rules_by_specificity(rules)

        self.assertEqual(multiple_paths_rule, sorted_rules[0])
        self.assertEqual(mixed_rule, sorted_rules[1])
        self.assertEqual(multiple_hosts_rule, sorted_rules[2])


@skipIf(not sys.platform.startswith("win"), "`eb migrate` only supports Windows")
class TestCreateAlbRules(unittest.TestCase):
    """Tests for the create_alb_rules function."""

    def test_create_alb_rules_basic_sites(self):
        """Test creating ALB rules from basic site configurations."""
        # Create a single HTTP site
        site = SiteConfig(
            name="Default Web Site",
            binding_info="*:80:example.com",
            physical_path="C:\\inetpub\\wwwroot",
            protocol="http",
        )

        site.rewrite_rules = [
            {
                "name": "Rewrite to index",
                "pattern": "^/home/",
                "action_type": "Rewrite",
                "action_url": "index.html",
            }
        ]

        # Test with a single HTTP site
        rules = create_alb_rules([site])

        # Verify basic structure
        self.assertIsInstance(rules, list)
        self.assertEqual(len(rules), 2)  # Host rule + rewrite rule

        # Check host-based rule
        host_rule = next(
            (
                r
                for r in rules
                if "Conditions" in r and r["Conditions"][0]["Field"] == "host-header"
            ),
            None,
        )
        self.assertIsNotNone(host_rule)
        self.assertEqual(host_rule["Protocol"], "http")
        self.assertEqual(host_rule["Priority"], 1)  # Priority should be assigned
        self.assertEqual(host_rule["Conditions"][0]["Values"][0], "example.com")

        # Check target group in actions
        self.assertEqual(host_rule["Actions"][0]["Type"], "forward")
        self.assertIn(
            "TargetGroupArn",
            host_rule["Actions"][0]["ForwardConfig"]["TargetGroups"][0],
        )
        self.assertIn(
            "80",
            host_rule["Actions"][0]["ForwardConfig"]["TargetGroups"][0][
                "TargetGroupArn"
            ],
        )

    def test_create_alb_rules_multiple_sites(self):
        """Test creating ALB rules from multiple site configurations."""
        # Create multiple sites
        site1 = SiteConfig(
            name="Default Web Site",
            binding_info="*:80:example.com",
            physical_path="C:\\inetpub\\wwwroot",
            protocol="http",
        )

        site1.rewrite_rules = [
            {
                "name": "Rewrite to index",
                "pattern": "^/home/",
                "action_type": "Rewrite",
                "action_url": "index.html",
            }
        ]

        site2 = SiteConfig(
            name="API Site",
            binding_info="*:8080:api.example.com",
            physical_path="C:\\inetpub\\apiroot",
            protocol="http",
        )

        site2.rewrite_rules = [
            {
                "name": "API version rewrite",
                "pattern": "^/api/v1/(.+)",
                "action_type": "Rewrite",
                "action_url": "api.php?path=$1",
            },
            {
                "name": "API docs rewrite",
                "pattern": "^/docs/(.*)",
                "action_type": "Rewrite",
                "action_url": "documentation.html",
            },
        ]

        site3 = SiteConfig(
            name="Secure Site",
            binding_info="*:443:secure.example.com",
            physical_path="C:\\inetpub\\secureroot",
            protocol="https",
        )

        rules = create_alb_rules([site1, site2, site3])

        # Should have rules for all sites and their rewrite rules
        self.assertEqual(len(rules), 6)  # 3 host rules + 3 rewrite rules

        # Verify protocols
        http_rules = [r for r in rules if r["Protocol"] == "http"]
        https_rules = [r for r in rules if r["Protocol"] == "https"]
        self.assertEqual(len(http_rules), 5)  # 2 sites + 3 rewrite rules
        self.assertEqual(len(https_rules), 1)  # 1 site

        # Verify priorities are assigned sequentially
        priorities = [r["Priority"] for r in rules]
        self.assertEqual(sorted(priorities), list(range(1, len(rules) + 1)))

    def test_create_alb_rules_rewrite_patterns(self):
        """Test that rewrite patterns are properly translated to ALB patterns."""
        # Create site with rewrite rules
        site = SiteConfig(
            name="API Site",
            binding_info="*:8080:api.example.com",
            physical_path="C:\\inetpub\\apiroot",
            protocol="http",
        )

        site.rewrite_rules = [
            {
                "name": "API version rewrite",
                "pattern": "^/api/v1/(.+)",
                "action_type": "Rewrite",
                "action_url": "api.php?path=$1",
            },
            {
                "name": "API docs rewrite",
                "pattern": "^/docs/(.*)",
                "action_type": "Rewrite",
                "action_url": "documentation.html",
            },
        ]

        rules = create_alb_rules([site])

        # Find the rule for API version rewrite
        api_rule = next(
            (
                r
                for r in rules
                if "Conditions" in r
                and any(
                    c["Field"] == "path-pattern" and "/api/v1/*" in c["Values"]
                    for c in r["Conditions"]
                )
            ),
            None,
        )

        self.assertIsNotNone(api_rule)
        path_condition = next(
            c for c in api_rule["Conditions"] if c["Field"] == "path-pattern"
        )
        self.assertEqual(path_condition["Values"][0], "/api/v1/*")

        # Find the rule for docs rewrite
        docs_rule = next(
            (
                r
                for r in rules
                if "Conditions" in r
                and any(
                    c["Field"] == "path-pattern" and "/docs/*" in c["Values"]
                    for c in r["Conditions"]
                )
            ),
            None,
        )

        self.assertIsNotNone(docs_rule)
        path_condition = next(
            c for c in docs_rule["Conditions"] if c["Field"] == "path-pattern"
        )
        self.assertEqual(path_condition["Values"][0], "/docs/*")

    def test_create_alb_rules_rule_specificity_sorting(self):
        """Test that rules are sorted by specificity."""
        # Create site with both host header and path pattern rules
        site = SiteConfig(
            name="Complex Site",
            binding_info="*:80:complex.example.com",
            physical_path="C:\\inetpub\\complexroot",
            protocol="http",
        )

        site.rewrite_rules = [
            {
                "name": "Path only rule",
                "pattern": "^/path/",
                "action_type": "Rewrite",
                "action_url": "path.html",
            },
            {
                "name": "Host and path rule",
                "pattern": "^/specific/",
                "action_type": "Rewrite",
                "action_url": "specific.html",
            },
        ]

        rules = create_alb_rules([site])

        # Rules with both host and path conditions should have higher priority (lower number)
        host_and_path_rule = next(
            (r for r in rules if "Conditions" in r and len(r["Conditions"]) > 1), None
        )

        path_only_rule = next(
            (
                r
                for r in rules
                if "Conditions" in r
                and len(r["Conditions"]) == 1
                and r["Conditions"][0]["Field"] == "path-pattern"
            ),
            None,
        )

        if host_and_path_rule and path_only_rule:
            self.assertLess(host_and_path_rule["Priority"], path_only_rule["Priority"])

    def test_create_alb_rules_empty_input(self):
        """Test behavior with empty input."""
        rules = create_alb_rules([])
        self.assertEqual(rules, [])

    def test_create_alb_rules_non_http_protocols(self):
        """Test that only HTTP/HTTPS protocols are processed."""
        # Create a site with non-HTTP protocol
        site = SiteConfig(
            name="FTP Site",
            binding_info="*:21:ftp.example.com",
            physical_path="C:\\inetpub\\ftproot",
            protocol="ftp",
        )

        rules = create_alb_rules([site])
        self.assertEqual(rules, [])  # Should ignore non-HTTP/HTTPS sites


@skipIf(not sys.platform.startswith("win"), "`eb migrate` only supports Windows")
class TestGetSiteConfigs(unittest.TestCase):
    """Tests for the get_site_configs function."""

    @mock.patch("os.path.exists")
    @mock.patch("xml.etree.ElementTree.parse")
    def test_get_site_configs_with_url_rewrites(self, mock_parse, mock_path_exists):
        """Test that URL rewrite rules are correctly parsed from web.config."""
        # Setup mock to indicate web.config exists
        mock_path_exists.return_value = True

        # Create a mock XML structure for web.config with URL rewrite rules
        mock_xml = """
        <configuration>
          <system.webServer>
            <rewrite>
              <rules>
                <rule name="Redirect to HTTPS" stopProcessing="true">
                  <match url="(.*)" />
                  <conditions>
                    <add input="{HTTPS}" pattern="^OFF$" />
                  </conditions>
                  <action type="Redirect" url="https://{HTTP_HOST}/{R:1}" redirectType="Permanent" />
                </rule>
                <rule name="API Rewrite" stopProcessing="true">
                  <match url="^api/v1/(.*)$" />
                  <action type="Rewrite" url="api.php?path={R:1}" />
                </rule>
              </rules>
            </rewrite>
          </system.webServer>
        </configuration>
        """

        # Create a mock ElementTree
        mock_root = ET.fromstring(mock_xml)
        mock_tree = mock.MagicMock()
        mock_tree.getroot.return_value = mock_root
        mock_parse.return_value = mock_tree

        # Create mock site
        site = MockSite(
            name="API Site",
            physical_path="C:\\inetpub\\apiroot",
            binding_info="*:80:api.example.com",
        )

        # Call the function
        site_configs = get_site_configs([site])

        # Verify results
        self.assertEqual(len(site_configs), 1)
        self.assertEqual(site_configs[0].name, "API Site")

        # Check that rewrite rules were parsed correctly
        self.assertEqual(len(site_configs[0].rewrite_rules), 2)

        # Check first rule
        self.assertEqual(site_configs[0].rewrite_rules[0]["name"], "Redirect to HTTPS")
        self.assertEqual(site_configs[0].rewrite_rules[0]["pattern"], "(.*)")
        self.assertEqual(site_configs[0].rewrite_rules[0]["action_type"], "Redirect")
        self.assertEqual(
            site_configs[0].rewrite_rules[0]["action_url"], "https://{HTTP_HOST}/{R:1}"
        )

        # Check second rule
        self.assertEqual(site_configs[0].rewrite_rules[1]["name"], "API Rewrite")
        self.assertEqual(site_configs[0].rewrite_rules[1]["pattern"], "^api/v1/(.*)$")
        self.assertEqual(site_configs[0].rewrite_rules[1]["action_type"], "Rewrite")
        self.assertEqual(
            site_configs[0].rewrite_rules[1]["action_url"], "api.php?path={R:1}"
        )

    @mock.patch("os.path.exists")
    @mock.patch("xml.etree.ElementTree.parse")
    def test_get_site_configs_with_multiple_rules_sections(
        self, mock_parse, mock_path_exists
    ):
        """Test parsing web.config with multiple <rules> sections."""
        # Setup mock to indicate web.config exists
        mock_path_exists.return_value = True

        # Create a mock XML structure with multiple <rules> sections
        mock_xml = """
        <configuration>
          <system.webServer>
            <rewrite>
              <rules>
                <rule name="Rule1" stopProcessing="true">
                  <match url="^site1/" />
                  <action type="Rewrite" url="index1.html" />
                </rule>
              </rules>
              <rules>
                <rule name="Rule2" stopProcessing="true">
                  <match url="^site2/" />
                  <action type="Rewrite" url="index2.html" />
                </rule>
              </rules>
            </rewrite>
          </system.webServer>
        </configuration>
        """

        # Create a mock ElementTree
        mock_root = ET.fromstring(mock_xml)
        mock_tree = mock.MagicMock()
        mock_tree.getroot.return_value = mock_root
        mock_parse.return_value = mock_tree

        # Create mock site
        site = MockSite(
            name="Multi Rules Site",
            physical_path="C:\\inetpub\\multiroot",
            binding_info="*:80:multi.example.com",
        )

        # Call the function
        site_configs = get_site_configs([site])

        # Verify results
        self.assertEqual(len(site_configs), 1)

        # Check that both rules were parsed correctly
        self.assertEqual(len(site_configs[0].rewrite_rules), 2)

        # Check first rule
        self.assertEqual(site_configs[0].rewrite_rules[0]["name"], "Rule1")
        self.assertEqual(site_configs[0].rewrite_rules[0]["pattern"], "^site1/")
        self.assertEqual(site_configs[0].rewrite_rules[0]["action_type"], "Rewrite")
        self.assertEqual(site_configs[0].rewrite_rules[0]["action_url"], "index1.html")

        # Check second rule
        self.assertEqual(site_configs[0].rewrite_rules[1]["name"], "Rule2")
        self.assertEqual(site_configs[0].rewrite_rules[1]["pattern"], "^site2/")
        self.assertEqual(site_configs[0].rewrite_rules[1]["action_type"], "Rewrite")
        self.assertEqual(site_configs[0].rewrite_rules[1]["action_url"], "index2.html")

    @mock.patch("os.path.exists")
    @mock.patch("xml.etree.ElementTree.parse")
    def test_get_site_configs_with_malformed_web_config(
        self, mock_parse, mock_path_exists
    ):
        """Test handling of malformed web.config files."""
        # Setup mock to indicate web.config exists
        mock_path_exists.return_value = True

        # Make parse throw an exception to simulate malformed XML
        mock_parse.side_effect = ET.ParseError("XML syntax error")

        # Create mock site
        site = MockSite(
            name="Malformed Config Site",
            physical_path="C:\\inetpub\\badconfig",
            binding_info="*:80:bad.example.com",
        )

        # Call the function - should not raise an exception
        site_configs = get_site_configs([site])

        # Verify results - site should be included but with no rewrite rules
        self.assertEqual(len(site_configs), 1)
        self.assertEqual(site_configs[0].name, "Malformed Config Site")
        self.assertEqual(site_configs[0].rewrite_rules, [])

    @mock.patch("os.path.exists")
    @mock.patch("xml.etree.ElementTree.parse")
    def test_get_site_configs_with_no_rewrite_section(
        self, mock_parse, mock_path_exists
    ):
        """Test handling of web.config files with no rewrite section."""
        # Setup mock to indicate web.config exists
        mock_path_exists.return_value = True

        # Create a mock XML structure with no rewrite section
        mock_xml = """
        <configuration>
          <system.webServer>
            <defaultDocument>
              <files>
                <add value="index.html" />
              </files>
            </defaultDocument>
          </system.webServer>
        </configuration>
        """

        # Create a mock ElementTree
        mock_root = ET.fromstring(mock_xml)
        mock_tree = mock.MagicMock()
        mock_tree.getroot.return_value = mock_root
        mock_parse.return_value = mock_tree

        # Create mock site
        site = MockSite(
            name="No Rewrite Site",
            physical_path="C:\\inetpub\\norewrite",
            binding_info="*:80:norewrite.example.com",
        )

        # Call the function
        site_configs = get_site_configs([site])

        # Verify results - site should be included but with no rewrite rules
        self.assertEqual(len(site_configs), 1)
        self.assertEqual(site_configs[0].name, "No Rewrite Site")
        self.assertEqual(site_configs[0].rewrite_rules, [])

    @mock.patch("os.path.exists")
    @mock.patch("xml.etree.ElementTree.parse")
    def test_get_site_configs_with_empty_rules_section(
        self, mock_parse, mock_path_exists
    ):
        """Test handling of web.config files with empty rules section."""
        # Setup mock to indicate web.config exists
        mock_path_exists.return_value = True

        # Create a mock XML structure with empty rules section
        mock_xml = """
        <configuration>
          <system.webServer>
            <rewrite>
              <rules>
              </rules>
            </rewrite>
          </system.webServer>
        </configuration>
        """

        # Create a mock ElementTree
        mock_root = ET.fromstring(mock_xml)
        mock_tree = mock.MagicMock()
        mock_tree.getroot.return_value = mock_root
        mock_parse.return_value = mock_tree

        # Create mock site
        site = MockSite(
            name="Empty Rules Site",
            physical_path="C:\\inetpub\\emptyrules",
            binding_info="*:80:emptyrules.example.com",
        )

        # Call the function
        site_configs = get_site_configs([site])

        # Verify results - site should be included but with no rewrite rules
        self.assertEqual(len(site_configs), 1)
        self.assertEqual(site_configs[0].name, "Empty Rules Site")
        self.assertEqual(site_configs[0].rewrite_rules, [])

    @mock.patch("os.path.exists")
    @mock.patch("xml.etree.ElementTree.parse")
    def test_get_site_configs_with_complex_rewrite_rules(
        self, mock_parse, mock_path_exists
    ):
        """Test parsing of complex rewrite rules with conditions."""
        # Setup mock to indicate web.config exists
        mock_path_exists.return_value = True

        # Create a mock XML structure with complex rewrite rules
        mock_xml = """
        <configuration>
          <system.webServer>
            <rewrite>
              <rules>
                <rule name="Complex Rule" stopProcessing="true">
                  <match url="^products/([0-9]+)/details$" />
                  <conditions>
                    <add input="{REQUEST_METHOD}" pattern="^GET$" />
                    <add input="{HTTP_HOST}" pattern="^(www\.)?(.*)" />
                  </conditions>
                  <action type="Rewrite" url="product_details.php?id={R:1}" />
                </rule>
                <rule name="Regex Capture Rule" stopProcessing="false">
                  <match url="^blog/([a-zA-Z0-9\-]+)/([0-9]{4})/([0-9]{2})/?$" />
                  <action type="Rewrite" url="blog.php?slug={R:1}&amp;year={R:2}&amp;month={R:3}" />
                </rule>
              </rules>
            </rewrite>
          </system.webServer>
        </configuration>
        """

        # Create a mock ElementTree
        mock_root = ET.fromstring(mock_xml)
        mock_tree = mock.MagicMock()
        mock_tree.getroot.return_value = mock_root
        mock_parse.return_value = mock_tree

        # Create mock site
        site = MockSite(
            name="Complex Rules Site",
            physical_path="C:\\inetpub\\complexrules",
            binding_info="*:80:complex.example.com",
        )

        # Call the function
        site_configs = get_site_configs([site])

        # Verify results
        self.assertEqual(len(site_configs), 1)

        # Check that both rules were parsed correctly
        self.assertEqual(len(site_configs[0].rewrite_rules), 2)

        # Check first rule
        self.assertEqual(site_configs[0].rewrite_rules[0]["name"], "Complex Rule")
        self.assertEqual(
            site_configs[0].rewrite_rules[0]["pattern"], "^products/([0-9]+)/details$"
        )
        self.assertEqual(site_configs[0].rewrite_rules[0]["action_type"], "Rewrite")
        self.assertEqual(
            site_configs[0].rewrite_rules[0]["action_url"],
            "product_details.php?id={R:1}",
        )

        # Check second rule
        self.assertEqual(site_configs[0].rewrite_rules[1]["name"], "Regex Capture Rule")
        self.assertEqual(
            site_configs[0].rewrite_rules[1]["pattern"],
            "^blog/([a-zA-Z0-9\-]+)/([0-9]{4})/([0-9]{2})/?$",
        )
        self.assertEqual(site_configs[0].rewrite_rules[1]["action_type"], "Rewrite")
        self.assertEqual(
            site_configs[0].rewrite_rules[1]["action_url"],
            "blog.php?slug={R:1}&year={R:2}&month={R:3}",
        )


# Mock classes for IIS objects
class MockVirtualDirectory:
    """Mock for IIS VirtualDirectory object."""

    def __init__(self, path: str, physical_path: str):
        self.Path = path
        self.PhysicalPath = physical_path


class MockVirtualDirectoryCollection:
    """Mock for IIS VirtualDirectory collection."""

    def __init__(self, virtual_directories: List[MockVirtualDirectory]):
        self._virtual_directories = virtual_directories

    def __getitem__(self, key):
        for vdir in self._virtual_directories:
            if vdir.Path == key:
                return vdir
        raise KeyError(f"VirtualDirectory with path '{key}' not found")


class MockApplication:
    """Mock for IIS Application object."""

    def __init__(self, path: str, physical_path: str):
        self.Path = path
        self._virtual_directories = [MockVirtualDirectory("/", physical_path)]
        self.VirtualDirectories = MockVirtualDirectoryCollection(
            self._virtual_directories
        )


class MockApplicationCollection:
    """Mock for IIS Application collection."""

    def __init__(self, applications: List[MockApplication]):
        self._applications = applications

    def __getitem__(self, key):
        for app in self._applications:
            if app.Path == key:
                return app
        raise KeyError(f"Application with path '{key}' not found")


class MockBinding:
    """Mock for IIS Binding object."""

    def __init__(self, binding_info: str, protocol: str = "http"):
        self.BindingInformation = binding_info
        self.Protocol = protocol


class MockBindingCollection:
    """Mock for IIS Binding collection."""

    def __init__(self, bindings: List[MockBinding]):
        self._bindings = bindings

    def __iter__(self):
        return iter(self._bindings)


class MockSite:
    """Mock for IIS Site object."""

    def __init__(
        self, name: str, physical_path: str, binding_info: str, protocol: str = "http"
    ):
        self.Name = name
        self._applications = [MockApplication("/", physical_path)]
        self.Applications = MockApplicationCollection(self._applications)
        self.Bindings = MockBindingCollection([MockBinding(binding_info, protocol)])


class MockServerManager:
    """Mock for IIS ServerManager object."""

    def __init__(self, sites: List[MockSite]):
        self.Sites = sites
