HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<div class="separator" style="clear: both;"><a href="https://www.khaleejtimes.com/" style="display: block; padding: 1em 0; text-align: center; ">
<img alt="" border="0" width="100" data-original-height="128" data-original-width="128" src="{{data.logo}}"/></a>
</div>

<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta name="description" content="{{data.job_summary}}">
    <meta name="keywords" content="{{data.keywords}}">
    <title>{{data.title}} at {{data.shortName}} - {{data.jobCountry}}</title>
    <style>
        #expiry-info {
            font-size: 18px;
        }

        #countdown.expired {
            color: red;
        }

        .apply-button {
            font-family: 'Roboto', sans-serif;
            background-color: #007bff;
            color: white;
            padding: 15px 30px;
            border: none;
            border-radius: 5px;
            cursor: pointer;
            font-size: 18px;
        }

        .apply-button:hover {
            background-color: #0056b3;
        }
    </style>
    <script type="application/ld+json">
        {
            "@context": "https://schema.org/",
            "@type": "JobPosting",
            "title": "{{data.title}} at {{data.shortName}} - {{data.jobCountry}}",
            "description": "<p>About {{data.shortName}}:</p><p>{{data.aboutOrg}}</p><p>Job Summary:</p><p>{{data.job_summary}}</p><p>Job Details:</p>{{data.descriptionHtml_Schema}}",
            "identifier": {
                "@type": "PropertyValue",
                "name": "KhaleejJobs",
                "value": "{{data.jobValue_id}}"
            },
            "hiringOrganization": {
                "@type": "Organization",
                "name": "{{data.longName}}",
                "sameAs": "{{data.orgWeb}}",
                "logo": "{{data.logo}}"
            },
            "directApply": false,
            "experienceInPlaceOfEducation": false,
            "industry": "{{data.job_industry}}",
            "occupationalCategory": "{{data.occupationalCategory}}",
            "workHours": "8am-5pm",
            "employmentType": "{{data.employmentType}}",
            "datePosted": "{{data.datePosted}}",
            "validThrough": "{{data.validThrough}}",
            "jobBenefits": "{{data.jobBenefits}}",
            "jobLocation": {
                "@type": "Place",
                "address": {
                    "@type": "PostalAddress",
                    "streetAddress": "{{data.streetAddress}}",
                    "addressLocality": "{{data.addressLocality}}",
                    "postalCode": "{{data.postalCode}}",
                    "addressCountry": "{{data.addressCountryISO}}",
                    "addressRegion": "{{data.addressRegion}}"
                }
            },
            "baseSalary": {
                "@type": "MonetaryAmount",
                "currency": "{{data.currency}}",
                "value": {
                    "@type": "QuantitativeValue",
                    "unitText": "{{data.salaryunittext}}",
                    "minValue": {{data.minSalary}},
                    "maxValue": {{data.maxSalary}}
                }
            },
            "estimatedSalary": {
                "@type": "MonetaryAmount",
                "currency": "{{data.currency}}",
                "value": {
                    "@type": "QuantitativeValue",
                    "unitText": "{{data.salaryunittext}}",
                    "minValue": 0,
                    "maxValue": 0
                }
            },
            "responsibilities": {{data.responsibilities}},
            "skills": {{data.skills}},
            "qualifications": {{data.qualifications}},
            "educationRequirements": [{
                "@type": "EducationalOccupationalCredential",
                "credentialCategory": "{{data.EducationalOccupationalCredential_Category}}"
            }],
            "experienceRequirements": {
                "@type": "OccupationalExperienceRequirements",
                "monthsOfExperience": {{data.MonthsOfExperience}}           
            }
        }
    </script>
</head>

<body>
    <p id="expiry-info"></p>
    <main>
        <p><strong>About {{data.shortName}}:</strong></p>
        <p>{{data.aboutOrg}}</p>
        <p><strong>Job Summary:</strong></p>
        <p>{{data.job_summary}}</p>
        <p><strong>Job Details:</strong></p>
        {{data.descriptionHtml_body}}
    </main><br>
    <button class="apply-button" onclick="handleApply('{{data.applyURL}}')">Apply Now</button>

    <script>
        function handleApply(url) {
            if (validateEmail(url)) {
                const confirmed = confirm(`Apply to this job using the email address: ${url}?`);
                if (confirmed) {
                    copyToClipboard(url);
                    alert('Email copied to clipboard! Apply using your email client.');
                }
            } else {
                window.open(url, '_blank');
            }
        }

        function validateEmail(email) {
            const re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
            return re.test(email);
        }

        function copyToClipboard(text) {
            const tempInput = document.createElement('input');
            tempInput.value = text;
            document.body.appendChild(tempInput);
            tempInput.select();
            document.execCommand('copy');
            document.body.removeChild(tempInput);
        }
    </script>

    <script>
        const expiryDate = new Date("{{data.validThrough}}");
        const expiryInfoElement = document.getElementById("expiry-info");
        const expiredMessage = document.createElement('div');
        expiredMessage.textContent = "This Job Post Expired";
        expiredMessage.style.color = "red";
        expiredMessage.style.fontWeight = "bold";
        expiredMessage.style.display = "none";
        expiryInfoElement.after(expiredMessage);
        let blinkInterval;

        function updateExpiryInfo() {
            const now = new Date();
            const userTimeZone = Intl.DateTimeFormat().resolvedOptions().timeZone;
            const expiryDateUserTimeZone = new Date(expiryDate.toLocaleString('en-US', {
                timeZone: userTimeZone
            }));
            const options = {
                weekday: 'short',
                day: 'numeric',
                month: 'short',
                year: 'numeric'
            };
            expiryInfoElement.innerHTML = `<b>Deadline:</b> ${expiryDateUserTimeZone.toLocaleDateString('en-US', options)} at ${expiryDateUserTimeZone.toLocaleTimeString('en-US')}`;

            if (now > expiryDate) {
                if (!blinkInterval) {
                    expiredMessage.style.display = "block";
                    blinkInterval = setInterval(() => {
                        expiredMessage.style.visibility = expiredMessage.style.visibility === "hidden" ? "visible" : "hidden";
                    }, 2000);
                }
            } else {
                clearInterval(blinkInterval);
                blinkInterval = null;
                expiredMessage.style.display = "none";
            }
        }

        updateExpiryInfo();
        setInterval(updateExpiryInfo, 1000);
    </script>
</body>

</html>
"""

# HTML template for remote jobs
HTML_REMOTE_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<div class="separator" style="clear: both;"><a href="https://www.khaleejtimes.com/" style="display: block; padding: 1em 0; text-align: center; ">
<img alt="" border="0" width="100" data-original-height="128" data-original-width="128" src="{{data.logo}}"/></a>
</div>

<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta name="description" content="{{data.job_summary}}">
    <meta name="keywords" content="{{data.keywords}}">
    <title>{{data.title}} at {{data.shortName}}, Remote - {{data.jobCountry}}</title>
    <style>
        #expiry-info {
            font-size: 18px;
        }

        #countdown.expired {
            color: red;
        }

        .apply-button {
            font-family: 'Roboto', sans-serif;
            background-color: #007bff;
            color: white;
            padding: 15px 30px;
            border: none;
            border-radius: 5px;
            cursor: pointer;
            font-size: 18px;
        }

        .apply-button:hover {
            background-color: #0056b3;
        }
    </style>
    <script type="application/ld+json">
        {
            "@context": "https://schema.org/",
            "@type": "JobPosting",
            "title": "{{data.title}} at {{data.shortName}}, Remote - {{data.jobCountry}}",
            "description": "<p>About {{data.shortName}}:</p><p>{{data.aboutOrg}}</p><p>Job Summary:</p><p>{{data.job_summary}}</p><p>Job Details:</p>{{data.descriptionHtml_Schema}}",
            "identifier": {
                "@type": "PropertyValue",
                "name": "KhaleejJobs",
                "value": "{{data.jobValue_id}}"
            },
            "hiringOrganization": {
                "@type": "Organization",
                "name": "{{data.longName}}",
                "sameAs": "{{data.orgWeb}}",
                "logo": "{{data.logo}}"
            },
            "directApply": false,
            "experienceInPlaceOfEducation": false,
            "industry": "{{data.job_industry}}",
            "occupationalCategory": "{{data.occupationalCategory}}",
            "workHours": "Flexible hours",
            "employmentType": "{{data.employmentType}}",
            "datePosted": "{{data.datePosted}}",
            "validThrough": "{{data.validThrough}}",
            "jobBenefits": "{{data.jobBenefits}}",
            "applicantLocationRequirements": {
                "@type": "Country",
                "name": "{{data.jobCountry}}"
            },
            "jobLocationType": "TELECOMMUTE",
            "baseSalary": {
                "@type": "MonetaryAmount",
                "currency": "{{data.currency}}",
                "value": {
                    "@type": "QuantitativeValue",
                    "unitText": "{{data.salaryunittext}}",
                    "minValue": {{data.minSalary}},
                    "maxValue": {{data.maxSalary}}
                }
            },
            "estimatedSalary": {
                "@type": "MonetaryAmount",
                "currency": "{{data.currency}}",
                "value": {
                    "@type": "QuantitativeValue",
                    "unitText": "{{data.salaryunittext}}",
                    "minValue": 0,
                    "maxValue": 0
                }
            },
            "responsibilities": {{data.responsibilities}},
            "skills": {{data.skills}},
            "qualifications": {{data.qualifications}},
            "educationRequirements": [{
                "@type": "EducationalOccupationalCredential",
                "credentialCategory": "{{data.EducationalOccupationalCredential_Category}}"
            }],
            "experienceRequirements": {
                "@type": "OccupationalExperienceRequirements",
                "monthsOfExperience": {{data.MonthsOfExperience}}           
            }
        }
    </script>
</head>

<body>
    <p id="expiry-info"></p>
    <main>
        <p><strong>About {{data.shortName}}:</strong></p>
        <p>{{data.aboutOrg}}</p>
        <p><strong>Job Summary:</strong></p>
        <p>{{data.job_summary}}</p>
        <p><strong>Job Details:</strong></p>
        {{data.descriptionHtml_body}}
    </main><br>
    <button class="apply-button" onclick="handleApply('{{data.applyURL}}')">Apply Now</button>

    <script>
        function handleApply(url) {
            if (validateEmail(url)) {
                const confirmed = confirm(`Apply to this job using the email address: ${url}?`);
                if (confirmed) {
                    copyToClipboard(url);
                    alert('Email copied to clipboard! Apply using your email client.');
                }
            } else {
                window.open(url, '_blank');
            }
        }

        function validateEmail(email) {
            const re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
            return re.test(email);
        }

        function copyToClipboard(text) {
            const tempInput = document.createElement('input');
            tempInput.value = text;
            document.body.appendChild(tempInput);
            tempInput.select();
            document.execCommand('copy');
            document.body.removeChild(tempInput);
        }
    </script>

    <script>
        const expiryDate = new Date("{{data.validThrough}}");
        const expiryInfoElement = document.getElementById("expiry-info");
        const expiredMessage = document.createElement('div');
        expiredMessage.textContent = "This Job Post Expired";
        expiredMessage.style.color = "red";
        expiredMessage.style.fontWeight = "bold";
        expiredMessage.style.display = "none";
        expiryInfoElement.after(expiredMessage);
        let blinkInterval;

        function updateExpiryInfo() {
            const now = new Date();
            const userTimeZone = Intl.DateTimeFormat().resolvedOptions().timeZone;
            const expiryDateUserTimeZone = new Date(expiryDate.toLocaleString('en-US', {
                timeZone: userTimeZone
            }));
            const options = {
                weekday: 'short',
                day: 'numeric',
                month: 'short',
                year: 'numeric'
            };
            expiryInfoElement.innerHTML = `<b>Deadline:</b> ${expiryDateUserTimeZone.toLocaleDateString('en-US', options)} at ${expiryDateUserTimeZone.toLocaleTimeString('en-US')}`;

            if (now > expiryDate) {
                if (!blinkInterval) {
                    expiredMessage.style.display = "block";
                    blinkInterval = setInterval(() => {
                        expiredMessage.style.visibility = expiredMessage.style.visibility === "hidden" ? "visible" : "hidden";
                    }, 2000);
                }
            } else {
                clearInterval(blinkInterval);
                blinkInterval = null;
                expiredMessage.style.display = "none";
            }
        }

        updateExpiryInfo();
        setInterval(updateExpiryInfo, 1000);
    </script>
</body>

</html>
"""