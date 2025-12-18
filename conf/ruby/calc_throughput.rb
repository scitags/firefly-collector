
def filter(event)
  begin
    duration = event.get('[duration]')
    received = event.get('[usage][received]')
    sent = event.get('[usage][sent]')

    if duration > 0 then
      usage_bytes = [received, sent].max
      total_bytes = [received, sent].sum
      average_throughput = usage_bytes / duration
      event.set('[flow-lifecycle][throughput]', average_throughput)
      event.set('[flow-lifecycle][total_bytes]', total_bytes)
      return [event]
    else
      return [event]
    end
  rescue => exception 
    logger.warn('Error calculating throughput', duration => duration, :received => received, :sent => sent, :error => exception.message)
    return [event]
  end
end
