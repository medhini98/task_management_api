
# Errors, Causes, and Fixes (AWS Deploy)

## 1. `CannotPullContainerError: image Manifest does not contain descriptor matching platform 'linux/amd64'`

* **Symptom:** Service events showed repeated pull failures; tasks churned between PENDING/RUNNING.
* **Root cause:** Image was built on an Apple Silicon Mac (arm64) and pushed without an amd64 manifest; Fargate in ap-south-1 pulled `linux/amd64`.
* **Fix:**

  ```bash
  docker buildx create --use
  docker buildx build --platform linux/amd64 -t $IMAGE_URI --push .
  # (Re)deploy:
  aws ecs update-service --cluster taskapi-cluster --service taskapi-service --force-new-deployment
  ```

  Also ensured task def had:

  ```json
  "runtimePlatform": {"cpuArchitecture":"X86_64","operatingSystemFamily":"LINUX"}
  ```
* **Verify:** `aws ecr batch-get-image ... | jq '.images[0].imageManifest'` shows `"architecture":"amd64"`. Service reaches steady state.

---

## 2. Couldn’t fetch Public IP (ENI shows `None`)

* **Symptom:** `InvalidNetworkInterfaceId.Malformed` when describing ENI; `eni` query returned `None`.
* **Root cause:** JMESPath query variant didn’t match; sometimes attachment not yet fully populated; or lookup needed to pivot via private IP.
* **Fix:** Use a resilient, two-step fallback and ensure public networking is enabled.

  ```bash
  TASK_ARN=$(aws ecs list-tasks --cluster taskapi-cluster --service-name taskapi-service \
    --desired-status RUNNING --query 'taskArns[0]' --output text)

  ENI_ID=$(aws ecs describe-tasks --cluster taskapi-cluster --tasks "$TASK_ARN" \
    --query "tasks[0].attachments[?type=='ElasticNetworkInterface'].details[?name=='networkInterfaceId']|[0][0].value" \
    --output text)

  if [ -z "$ENI_ID" ] || [ "$ENI_ID" = "None" ]; then
    PRIV_IP=$(aws ecs describe-tasks --cluster taskapi-cluster --tasks "$TASK_ARN" \
      --query "tasks[0].containers[0].networkInterfaces[0].privateIpv4Address" --output text)
    ENI_ID=$(aws ec2 describe-network-interfaces \
      --filters Name=addresses.private-ip-address,Values="$PRIV_IP" \
      --query 'NetworkInterfaces[0].NetworkInterfaceId' --output text)
  fi

  aws ec2 describe-network-interfaces --network-interface-ids "$ENI_ID" \
    --query 'NetworkInterfaces[0].Association.PublicIp' --output text
  ```

  Networking prerequisites confirmed: **assignPublicIp=ENABLED**, public subnets with **IGW route**, open SG on port **8000**.
* **Verify:** `PublicIp` returns an IP; visiting `http://<IP>:8000/docs` works.

---

## 3. `aws ecs wait services-stable` hangs

* **Symptom:** Waiter runs “forever”.
* **Root cause:** Service wasn’t stabilizing due to the image pull error above.
* **Fix:** Always check events:

  ```bash
  aws ecs describe-services --cluster taskapi-cluster --services taskapi-service \
    --query 'services[0].events[0:10].[createdAt,message]' --output table
  ```

  Resolve the underlying event (usually image/permissions/networking), then re-run the waiter.

---

## 4. Swagger `/users` empty and `POST /todos/` 500 (bad `created_by`)

* **Symptom:** Creating a task with a hardcoded `created_by` UUID failed; `/users` returned `[]`.
* **Root cause:** In Fargate we used **SQLite** (file) for simplicity and **didn’t run seeding** in the container; therefore the referenced user didn’t exist.
* **Fix options:**

  * Add a lightweight **init step** to call `data_db.py` on container start, or
  * First create a user via API and use that `id` in `created_by`, or
  * Temporarily expose a `/seed` endpoint for demo use.
* **Verify:** `/users` returns seeded users; `POST /todos/` with a real `created_by` returns 201.

---

## 5. CloudWatch dashboard shows “No data available”

* **Symptom:** Custom dashboard tiles were empty.
* **Root cause:** The initial widgets targeted `ECS/ContainerInsights` before metrics were flowing; also needed traffic to generate data. The simpler namespace `AWS/ECS` already had CPU/Memory.
* **Fix:**

  * Use `AWS/ECS` metrics in `dashboard.json` (CPUUtilization, MemoryUtilization).
  * Generate traffic:

    ```bash
    for i in $(seq 1 200); do curl -s http://<PUBLIC_IP>:8000/healthz >/dev/null; done
    ```
  * (Optional) Enable Container Insights for richer metrics:

    ```bash
    aws ecs update-cluster-settings --cluster taskapi-cluster \
      --settings name=containerInsights,value=enabled
    ```
* **Verify:** CloudWatch → **Dashboards → TaskAPI-Overview** shows CPU/Memory lines; ECS automatic dashboards show cluster/service metrics.

---

## 6. Wrong command for alarms

* **Symptom:** `aws: [ERROR]: argument operation: Found invalid choice 'put-alarm'`
* **Root cause:** The correct subcommand is **`put-metric-alarm`**, not `put-alarm`.
* **Fix:**

  ```bash
  aws cloudwatch put-metric-alarm \
    --alarm-name TaskAPI-CPU-High \
    --metric-name CPUUtilization \
    --namespace AWS/ECS \
    --dimensions Name=ClusterName,Value=taskapi-cluster Name=ServiceName,Value=taskapi-service \
    --statistic Average --period 60 --threshold 80 --comparison-operator GreaterThanThreshold \
    --evaluation-periods 5 --treat-missing-data notBreaching
  ```

---

## 7. Log retrieval slow

* **Symptom:** `aws logs tail` felt sluggish.
* **Root cause:** Tail without narrowing time/limit on an active group is slow.
* **Fix:**

  ```bash
  aws logs tail /ecs/taskapi --since 10m --follow   # recent window
  # or filter:
  aws logs filter-log-events --log-group-name /ecs/taskapi --start-time $(($(date +%s)-600))000
  ```

---

## 8. Confusion validating image architecture

* **Symptom:** Unsure whether ECR tag was actually amd64.
* **Fix:** Inspect the manifest list:

  ```bash
  docker buildx imagetools inspect "$IMAGE_URI"
  aws ecr batch-get-image --repository-name $ECR_REPO --image-ids imageTag=latest \
    --query 'images[0].imageManifest' --output text | grep -A3 platform
  ```
* **Verify:** Shows `"architecture":"amd64","os":"linux"`.

---