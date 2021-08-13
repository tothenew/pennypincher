### Advanced settings
By default, the lambda takes into account last 14 days usage of the resources. The number of days to be considered for generating the report can be mentioned specifically for each resource in the CloudwatchConfig parameter while creating the cloudformation stack as follows:

![Alt](/images/main/advanced_configuration.png)

### Recommendation Logic

The following table lists the criteria kept to decide if the resource is idle or not and mentions the recommendations which can help in cost saving.

![Alt](/images/main/recommendation_criteria.png)

### Architecture Diagram 

![Alt](/images/main/penny_pincher_architecture_diagram.jpg)
